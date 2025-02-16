import io
import pandas as pd
from utils.missing_fields.fill import fix_missing_fields
from utils.logging_config import setup_logger

logger = setup_logger(__name__)

def process_value(x):

    """
        - assign zero if entity can't be processed 
    """
    if pd.isnull(x): return 0 
    elif isinstance(x, int): return x
    elif isinstance(x, float): return x
    
    elif isinstance(x, str):
        try: return float(x.replace('$', ''))  # Remove '$' and convert to float
        except ValueError: return 0
        
    else: return 0

def assign_unique_ids(df, column_name):

    """
        given a column, assigns unique ids to its values
    """
    new_column_name = f"{column_name} id"

    unique_values = [val for val in df[column_name].unique() if pd.notnull(val)]
    value_to_id = {val: idx+1 for idx, val in enumerate(unique_values)}
    df[new_column_name] = df[column_name].map(value_to_id)
    return df

def assign_linked_ids(merged_df, column_name, linkage_column_name, additional_column=None):
    
    # Step 1: Create a unique key based on provided columns
    if additional_column:
        merged_df['key'] = merged_df[linkage_column_name].astype(str) + '-' + merged_df[column_name].astype(str) + '-' + merged_df[additional_column].astype(str)
    else:
        merged_df['key'] = merged_df[linkage_column_name].astype(str) + '-' + merged_df[column_name].astype(str)

    # Step 2: Use factorize to assign unique numeric IDs
    merged_df[f'{column_name} id'] = pd.factorize(merged_df['key'])[0] + 1

    # Step 3: Drop the temporary key column
    merged_df.drop(columns=['key'], inplace=True)

    return merged_df

def process_online(filename, platform):
    
    # 1: Read and Merge Online Data
    data = pd.read_excel(filename, sheet_name=None)

    item = data['items']
    raw_modifier = data['modifiers']
    modifier = raw_modifier[['item_name', 'modifier_name', 'modifier_type', 'option_name', 'option_price']].drop_duplicates()

    merged_df = pd.merge(item, modifier, how='outer', left_on='Item Name', right_on='item_name')
    merged_df.drop('item_name', axis=1, inplace=True)

    merged_df = merged_df.rename(columns={ 'modifier_name': 'Modifier Name', 'option_name': 'Option Name', 'option_price': 'Option Price', 'modifier_type': 'Modifier Type' })

    # 2: Process Columns
    merged_df['Modifier Type'] = merged_df['Modifier Type'].apply( lambda x: True if pd.isnull(x) else (False if 'required' in x.lower() else True) )

    for i in ['Item Price', 'Option Price']:
        merged_df[i] = merged_df[i].apply(process_value)

    # 3: Sort Ids for Convenient Testing
    merged_df = merged_df.sort_values(by=['Category Name', 'Item Name', 'Modifier Name', 'Option Name'])

    merged_df['Category Name'] = pd.Categorical(merged_df['Category Name'], categories=item['Category Name'].unique(), ordered=True)
    merged_df = merged_df.sort_values('Category Name')

    merged_df['Category Name'] = merged_df['Category Name'].astype(str)

    # 4: Assign Ids
    merged_df = assign_unique_ids(merged_df, 'Category Name')

    if platform == 'Ubereats':
        merged_df = assign_linked_ids(merged_df, 'Item Name', 'Item Price', 'Item Description')
        merged_df = assign_linked_ids(merged_df, 'Modifier Name', 'Item Name id')
        merged_df = assign_linked_ids(merged_df, 'Option Name', 'Option Price')
    else:
        merged_df = assign_unique_ids(merged_df, 'Item Name')
        merged_df = assign_unique_ids(merged_df, 'Modifier Name')
        merged_df = assign_unique_ids(merged_df, 'Option Name')
    
    return merged_df, data['info']['Name']

def assigner(aio_format, merged_df):

    # 1: Assign Individual Sheets
    aio_format['Category'][['id', 'categoryName']] = merged_df[['Category Name id', 'Category Name']].dropna().drop_duplicates()
    aio_format['Item'][['id', 'itemName', 'itemDescription', 'itemPrice']] = merged_df[['Item Name id', 'Item Name', 'Item Description', 'Item Price']].drop_duplicates(subset=['Item Name id', 'Item Name', 'Item Price']).dropna(subset=['Item Name'])
    aio_format['Modifier'][['id', 'modifierName', 'isOptional']] = merged_df[['Modifier Name id', 'Modifier Name', 'Modifier Type']].dropna().drop_duplicates()
    aio_format['Modifier Option'][['id', 'optionName', 'price']] = merged_df[['Option Name id', 'Option Name', 'Option Price']].dropna().drop_duplicates()

    # 2: Assign Mapping Sheets
    merged_df = merged_df[['Category Name id', 'Item Name id', 'Modifier Name id', 'Option Name id']].sort_values(by=['Category Name id', 'Item Name id', 'Modifier Name id', 'Option Name id'], ascending=[True, True, True, True])

    aio_format['Category Items'][['categoryId', 'itemId']] = merged_df[['Category Name id', 'Item Name id']].dropna().drop_duplicates()
    aio_format['Category Items']['id'] = [i+1 for i in range(0, len(aio_format['Category Items']))]
    aio_format['Item Modifiers'][['itemId', 'modifierId']] = merged_df[['Item Name id', 'Modifier Name id']].dropna().drop_duplicates()
    aio_format['Modifier ModifierOptions'][['modifierId', 'modifierOptionId']] = merged_df[['Modifier Name id', 'Option Name id']].dropna().drop_duplicates()

    return aio_format

def process_online_only(filename, selected_value):

    # read aio format and process online menu
    aio_format = pd.read_excel("./resource/AIO Template.xlsx", sheet_name=None)
    merged_df, name = process_online(filename, selected_value)

    # file aio format menu and fill missing fields
    aio_format = assigner(aio_format, merged_df)
    new_format = fix_missing_fields(aio_format)

    # buffer excel file with multiple sheets
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        for key in new_format.keys():
            new_format[key].to_excel(writer, sheet_name=key, index=False)            
    output.seek(0)

    return output, name.values[0]