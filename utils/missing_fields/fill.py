import pandas as pd
from utils.logging_config import setup_logger

logger = setup_logger(__name__)

missing_fields = {
    'Menu': {
        'id': 1,
        'menuName': "Main Menu",
        'posDisplayName': "Main Menu",
        'sortOrder': 1,
        'posButtonColor': "#e34032"
    },
    'Category': {},
    'Category Items': {},
    'Item': {},
    'Item Modifiers': {},
    'Modifier': {},
    'Modifier ModifierOptions': {},
    'Modifier Option': {},

    'Modifier Group': {},
    'Category Modifiers': {},
    'Category ModifierGroups': {},
    'Item Modifier Group': {},

    'Setting': {},
    'Visibility Setting': {},
    'Day Schedule': {},

    'Allergen': {},
    'Tag': {},
}

def truncate_values_pos(df, column_name, max_length=16):
    return df[column_name].apply(lambda x: x[:max_length] if isinstance(x, str) else x)

def truncate_values_dashboard(df, column_name, max_length=45):
    return df[column_name].apply(lambda x: x[:max_length] if isinstance(x, str) and len(x) > max_length else x)

def read_or_create_sheet(filename, sheet_name):
    return filename[sheet_name]

def remove_quotations(column):
    return column.str.replace(r"[\'\"]", "", regex=True)

def fix_menu_sheet(dataframes, filename, sheetname):
    data = read_or_create_sheet(filename, sheet_name=sheetname)
    if 'menuName' not in data.columns or data['menuName'].isnull().all():
        for col in missing_fields[sheetname].keys():
            data[col] = [missing_fields[sheetname][col]]
    else:
        data['menuName'] = truncate_values_dashboard(data, 'menuName')
        data['posDisplayName'] = data['menuName']
        data['posButtonColor'] = ["#e34032"] * len(data)
        data['sortOrder'] = list(range(1, len(data) + 1))
    dataframes[sheetname] = data

def fix_category_sheet(dataframes, filename, sheetname):
    data = read_or_create_sheet(filename, sheet_name=sheetname)
    data['categoryName'] = remove_quotations(data['categoryName'])
    data['categoryName'] = truncate_values_dashboard(data, 'categoryName')
    category_names = data['categoryName'].tolist()

    # commented because online to aio tool's ids are getting overwritten and issues get hiden, causing maping to mix up
    #data['id'] = list(range(1, len(data) + 1))
    data['posDisplayName'] = category_names
    data['posDisplayName'] = remove_quotations(data['posDisplayName'])
    data['posDisplayName'] = truncate_values_pos(data, 'posDisplayName')

    data['kdsDisplayName'] = category_names
    data['kdsDisplayName'] = remove_quotations(data['kdsDisplayName'])
    data['sortOrder'] = list(range(1, len(data) + 1))
    if 'menuIds' not in data.columns or data['menuIds'].isnull().all():
        data['menuIds'] = [1] * len(data)

    data['color'] = ["#FFFFFF"] * len(data)
    data['image'] = ["https://my-kiosk.s3.us-west-2.amazonaws.com/Untitled+(60).png"] * len(data) 
    dataframes[sheetname] = data

def fix_category_items_sheet(dataframes, filename, sheetname):
    data = read_or_create_sheet(filename, sheet_name=sheetname)
    data['id'] = list(range(1, len(data) + 1))
    data['sortOrder'] = list(range(1, len(data) + 1))
    dataframes[sheetname] = data

def fix_items_sheet(dataframes, filename, sheetname):

    data = read_or_create_sheet(filename, sheet_name=sheetname)

    # commented because online to aio tool's ids are getting overwritten and issues get hiden, causing maping to mix up
    #data['id'] = list(range(1, len(data) + 1))
    data['itemName'] = remove_quotations(data['itemName'])
    data['itemName'] = truncate_values_dashboard(data, 'itemName')

    data['posDisplayName'] = data['itemName']
    data['posDisplayName'] = truncate_values_pos(data, 'posDisplayName')
    data['kdsName'] = data['itemName']

    data['orderQuantityLimit'] = ["TRUE"] * len(data)
    data['minLimit'] = [1] * len(data)
    data['maxLimit'] = [999] * len(data)

    data['isSpecialRequest'] = ["TRUE"] * len(data)
    data['taxLinkedWithParentSetting'] = ["TRUE"] * len(data)
    data['calculatePricesWithTaxIncluded'] = ["TRUE"] * len(data)

    data['stockStatus'] = ["inStock"] * len(data)
    data['saleCategory'] = ["Food Sales"] * len(data)

    data['noMaxLimit'] = ["FALSE"] * len(data)
    data['takeoutException'] = ["FALSE"] * len(data)
    data['inheritTagsFromCategory'] = ["FALSE"] * len(data)
    data['inheritModifiersFromCategory'] = ["FALSE"] * len(data)

    data['itemPrice'] = data['itemPrice'].apply(lambda x: x if pd.notnull(x) else 0)

    dataframes[sheetname] = data

def fix_item_modifiers(dataframes, filename, sheetname):
    data = read_or_create_sheet(filename, sheet_name=sheetname)
    data['sortOrder'] = list(range(1, len(data) + 1))
    dataframes[sheetname] = data

def fix_modifier_options(dataframes, filename, sheetname):
    data = read_or_create_sheet(filename, sheet_name=sheetname)
    data['optionName'] = remove_quotations(data['optionName'])
    data['optionName'] = truncate_values_dashboard(data, 'optionName')
    
    data['posDisplayName'] = data['optionName']
    data['posDisplayName'] = truncate_values_pos(data, 'posDisplayName')
    if 'price' not in data.columns or not pd.to_numeric(data['price'], errors='coerce').notnull().all():
        data['price'] = [0] * len(data)
    data['isStockAvailable'] = ["TRUE"] * len(data)
    data['isSizeModifier'] = ["FALSE"] * len(data)
    dataframes[sheetname] = data

def fix_modifier_modifier_options(dataframes, filename, sheetname):
    data = read_or_create_sheet(filename, sheet_name=sheetname)
    data['isDefaultSelected'] = ["FALSE"] * len(data)
    data['maxLimit'] = [1] * len(data)

    data2 = filename["Modifier"]
    data3 = filename["Modifier Option"]

    data = data.merge(data2[['id', 'modifierName', 'isNested']], left_on='modifierId', right_on='id', how='left', suffixes=('', '_data2'))
    data = data.merge(data3[['id', 'optionName']], left_on='modifierOptionId', right_on='id', how='left', suffixes=('', '_data3'))
    
    data['optionDisplayName'] = data.apply(lambda row: f"{row['optionName']} {row['modifierName']}" if row['isNested'] == "TRUE" else row['optionName'], axis=1)
    data['optionDisplayName'] = truncate_values_dashboard(data, 'optionDisplayName')
    
    data.drop(columns=['id', 'id_data3', 'modifierName', 'isNested', 'optionName'], inplace=True)

    dataframes[sheetname] = data

def fix_modifier_group(dataframes, filename, sheetname):
    data = read_or_create_sheet(filename, sheet_name=sheetname)
    data['onPrem'] = ["TRUE"] * len(data)
    data['offPrem'] = ["TRUE"] * len(data)
    data['groupName'] = truncate_values_dashboard(data, 'groupName')

    data['posDisplayName'] = data['groupName']
    dataframes[sheetname] = data

def fix_category_modifiers(dataframes, filename, sheetname):
    data = read_or_create_sheet(filename, sheet_name=sheetname)
    data['sortOrder'] = list(range(1, len(data) + 1))
    dataframes[sheetname] = data

def fix_category_modifier_group(dataframes, filename, sheetname):
    data = read_or_create_sheet(filename, sheet_name=sheetname)
    data['sortOrder'] = list(range(1, len(data) + 1))
    dataframes[sheetname] = data

def fix_item_modifier_group(dataframes, filename, sheetname):
    data = read_or_create_sheet(filename, sheet_name=sheetname)
    data['sortOrder'] = list(range(1, len(data) + 1))
    dataframes[sheetname] = data

def fix_tags(dataframes, sheetname):
    tags = pd.read_csv("./resource/Tag.csv")
    dataframes[sheetname] = tags

def fix_allergen(dataframes, sheetname):
    allergen = pd.read_csv("./resource/Allergen.csv")
    dataframes[sheetname] = allergen

def fix_modifier(dataframes, filename, sheetname):

    data = read_or_create_sheet(filename, sheet_name=sheetname)

    data['modifierName'] = remove_quotations(data['modifierName'])
    data['modifierName'] = truncate_values_dashboard(data, 'modifierName')

    data['posDisplayName'] = data['modifierName']
    data['posDisplayName'] = truncate_values_pos(data, 'posDisplayName')

    data['multiSelect'] = ["FALSE"] * len(data)
    data['isNested'] = ["FALSE"] * len(data)

    data['isOptional'] = data['isOptional'].apply(lambda x: "TRUE" if x != False else "FALSE")
    data['isSizeModifier'] = ["FALSE"] * len(data)

    data['limitIndividualModifierSelection'] = ["TRUE"] * len(data)

    df2 = filename["Modifier ModifierOptions"]
    modifier_counts = df2.groupby('modifierId').size().reset_index(name='count')
    data = data.merge(modifier_counts, left_on='id', right_on='modifierId', how='left')
    data['maxSelector'] = data['count'].fillna(0)
    data.drop(['count', 'modifierId'], axis=1, inplace=True)

    data['maxSelector'] = data.apply(lambda row: 1 if row['isOptional'] == "FALSE" else row['maxSelector'], axis=1)

    data['onPrem'] = ["TRUE"] * len(data)
    data['offPrem'] = ["TRUE"] * len(data)
    data['stockStatus'] = ["TRUE"] * len(data)

    data['addNested'] = ["FALSE"] * len(data)
    data['pizzaSelection'] = ["FALSE"] * len(data)
    data['noMaxSelection'] = ["FALSE"] * len(data)

    data['modifierOptionPriceType'] = ["Individual"] * len(data)
    data['minSelector'] = data['isOptional'].apply(lambda x: 1 if x == "FALSE" else 0)
    data['prefix'] = data['isNested'].apply(lambda x: None if x == "TRUE" else "Select any")
    data['canGuestSelectMoreModifiers'] = data['isOptional']

    dataframes[sheetname] = data

def add_remaining(dataframes, filename, sheetname):
    data = read_or_create_sheet(filename, sheet_name=sheetname)
    dataframes[sheetname] = data

def fix_missing_fields(filename):
    
    dataframes = {}

    fix_menu_sheet(dataframes, filename, "Menu")
    fix_category_sheet(dataframes, filename, "Category")
    fix_category_items_sheet(dataframes, filename, "Category Items")
    fix_items_sheet(dataframes, filename, "Item")
    fix_item_modifiers(dataframes, filename, "Item Modifiers")
    fix_modifier(dataframes, filename, "Modifier")
    fix_modifier_modifier_options(dataframes, filename, "Modifier ModifierOptions")
    fix_modifier_options(dataframes, filename, "Modifier Option")
    fix_modifier_group(dataframes, filename, "Modifier Group")
    fix_category_modifiers(dataframes, filename, "Category Modifiers")
    fix_category_modifier_group(dataframes, filename, "Category ModifierGroups")
    fix_item_modifier_group(dataframes, filename, "Item Modifier Group")

    fix_tags(dataframes, "Tag")
    fix_allergen(dataframes, "Allergen")

    add_remaining(dataframes, filename, "Setting")
    add_remaining(dataframes, filename, "Visibility Setting")
    add_remaining(dataframes, filename, "Day Schedule")
    
    logger.info("Filling in missing fields has been completed.")
    return dataframes