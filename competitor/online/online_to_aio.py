import io
import pandas as pd
from utils.missing_fields.fill import fix_missing_fields
from utils.logging_config import setup_logger

logger = setup_logger(__name__)

def assign_unique_ids(df, column_name):

    """
        given a column, assigns unique ids to its values
    """
    new_column_name = f"{column_name} id"

    unique_values = [val for val in df[column_name].unique() if pd.notnull(val)]
    value_to_id = {val: idx+1 for idx, val in enumerate(unique_values)}
    df[new_column_name] = df[column_name].map(value_to_id)
    return df

def process_value(x):

    if pd.isnull(x):
        return 0  # Assign as it is if null
    
    elif isinstance(x, int):
        return x  # Assign as it is if integer
    
    elif isinstance(x, float):
        return x  # Assign as it is if float
    
    elif isinstance(x, str):
        try: 
            return float(x.replace('$', ''))  # Remove '$' and convert to float
        except ValueError: 
            return None  # Assign null if conversion fails
        
    else:
        return None  # Assign null for unexpected types
            
def assign_linked_ids(merged_df, column_name, linkage_column_name):

    # make unique identifier using column and linkage
    key = f'{column_name} Key'
    merged_df[key] = merged_df[linkage_column_name].astype(str) + '-' + merged_df[column_name]
    uniques = merged_df[[key, linkage_column_name, column_name]].drop_duplicates().reset_index(drop=True)
    uniques.dropna(inplace=True)
    uniques = uniques.reset_index(drop=True)

    # assign id and reverse map
    uniques[f'{column_name} id'] = list(range(1, len(uniques) + 1)) # uniques.index + 1  
    df = merged_df.merge(uniques[[key, f'{column_name} id']], on=key, how='left')
    df.drop(key, inplace=True, axis=1)
    return df

def process_online(filename, platform):
    
    # read online available data and merge
    data = pd.read_excel(filename, sheet_name=None)

    item = data['items']
    raw_modifier = data['modifiers']
    modifier = raw_modifier[['item_name', 'modifier_name', 'modifier_type', 'option_name', 'option_price']].drop_duplicates()

    merged_df = pd.merge(item, modifier, how='outer', left_on='Item Name', right_on='item_name')
    merged_df.drop('item_name', axis=1, inplace=True)

    # process online data
    merged_df = merged_df.rename(columns={ 'modifier_name': 'Modifier Name', 'option_name': 'Option Name', 'option_price': 'Option Price', 'modifier_type': 'Modifier Type' })
    merged_df['Modifier Type'] = merged_df['Modifier Type'].apply( lambda x: True if pd.isnull(x) else (False if 'required' in x.lower() else True) )

    for i in ['Item Price', 'Option Price']:
        merged_df[i] = merged_df[i].apply(process_value)

    # if someone tests file via csv, its easier if ids are in sequence for particular category, item, modifier
    #merged_df = merged_df.sort_values(by=['Category Name', 'Item Name', 'Modifier Name', 'Option Name'])

    for i in ['Category Name']:
        merged_df = assign_unique_ids(merged_df, i)

    if platform == 'Ubereats':
        merged_df = assign_linked_ids(merged_df, 'Item Name', 'Item Price')
        merged_df = assign_linked_ids(merged_df, 'Modifier Name', 'Item Name id')
        merged_df = assign_linked_ids(merged_df, 'Option Name', 'Option Price')
    else:
        merged_df = assign_unique_ids(merged_df, 'Item Name')
        merged_df = assign_unique_ids(merged_df, 'Modifier Name')
        merged_df = assign_unique_ids(merged_df, 'Option Name')

    return merged_df, data['info']['Name']

def assigner(aio_format, merged_df):

    # assign individual data
    aio_format['Category'][['id', 'categoryName']] = merged_df[['Category Name id', 'Category Name']].dropna().drop_duplicates()

    # ISSUE: as an item had same price, but with different categories it had different description
    # when it passes through UberEats, it uses assign_linked_ids so tehy get assigned same ids
    # when it passes through missing field it reassigns ids based on separate row
    # merged_df[['Item Name id', 'Item Name', 'Item Price']] = merged_df[['Item Name id', 'Item Name', 'Item Price']].drop_duplicates()
    aio_format['Item'][['id', 'itemName', 'itemDescription', 'itemPrice']] = merged_df[['Item Name id', 'Item Name', 'Item Description', 'Item Price']].drop_duplicates()
    aio_format['Item'] = aio_format['Item'].dropna(subset=['itemName'])

    aio_format['Modifier'][['id', 'modifierName', 'isOptional']] = merged_df[['Modifier Name id', 'Modifier Name', 'Modifier Type']].dropna().drop_duplicates()
    merged_df['Option Price'] = merged_df['Option Price'].fillna(0)
    aio_format['Modifier Option'][['id', 'optionName', 'price']] = merged_df[['Option Name id', 'Option Name', 'Option Price']].dropna().drop_duplicates()

    # assign mapping data
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