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
        return x  # Assign as it is if null
    
    elif isinstance(x, int):
        return x  # Assign as it is if integer
    
    elif isinstance(x, str):
        try: return float(x.replace('$', ''))  # Remove '$' and convert to float
        except ValueError: return None  # Assign null if conversion fails
        
    else:
        return None  # Assign null for unexpected types
            
def process_online(filename):
    
    # read online available data and merge
    data = pd.read_excel(filename, sheet_name=None)

    item = data['items']
    raw_modifier = data['modifiers']
    modifier = raw_modifier[['item_name', 'modifier_name', 'modifier_type', 'option_name', 'option_price']].drop_duplicates()

    merged_df = pd.merge(item, modifier, how='outer', left_on='Item Name', right_on='item_name')

    # process online data
    merged_df.drop('item_name', axis=1, inplace=True)
    merged_df = merged_df.rename(columns={ 'modifier_name': 'Modifier Name', 'option_name': 'Option Name', 'option_price': 'Option Price', 'modifier_type': 'Modifier Type' })
    merged_df['Modifier Type'] = merged_df['Modifier Type'].apply(lambda x: "False" if x == 'Required' else "True")

    #for i in ['Item Price', 'Option Price']:
    #    merged_df[i] = merged_df[i].apply(lambda x: float(x.replace('$', '')) if pd.notnull(x) else x)    

    for i in ['Item Price', 'Option Price']:
        merged_df[i] = merged_df[i].apply(process_value)

    for i in ['Category Name', 'Item Name', 'Modifier Name', 'Option Name']:
        merged_df = assign_unique_ids(merged_df, i)

    return merged_df, data['info']['Name']

def assigner(aio_format, merged_df):

    # assign individual data
    aio_format['Category'][['id', 'categoryName']] = merged_df[['Category Name id', 'Category Name']].dropna().drop_duplicates()
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

def process_online_only(filename):

    # read aio format and process online menu
    aio_format = pd.read_excel("./resource/AIO Template.xlsx", sheet_name=None)
    merged_df, name = process_online(filename)

    # file aio format menu and fill missing fields
    aio_format = assigner(aio_format, merged_df)
    new_format = fix_missing_fields(aio_format)

    # buffer excel file with multiple sheets
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        for key in new_format.keys():
            new_format[key].to_excel(writer, sheet_name=key, index=False)            
    output.seek(0)

    return output, name