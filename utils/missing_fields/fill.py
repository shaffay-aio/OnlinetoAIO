import pandas as pd
from utils.logging_config import setup_logger

logger = setup_logger(__name__)

missing_fields = {
    'Menu': {
        'id': 1,
        'menuName': "Main Menu",
        'posDisplayName': "Main Menu",
        #'menuDescription': "Main Menu",
        #'restaurantId': 1,
        'sortOrder': 1,
        'posButtonColor': "#e34032"
    },
    'Category': {
        'id': 7,
        'posDisplayName': 7,
        'kdsDisplayName': 7,
        'sortOrder': 7,
        'menuIds': 7
    },
    'Category Items': {
        'id': 7,
        'sortOrder': 7
    },
    'Item': {
        'id': 7,
        #'showOnMenu': 7,
        #'showOnline': 7,
        #'showPOS': 7,
        #'showQR': 7,
        #'showThirdParty': 7,
        'posDisplayName': 7,
        'kdsDisplayName': 7,
        'orderQuantityLimit': 7,
        'minLimit': 7,
        'maxLimit': 7,
        'noMaxLimit': 7

        # additional madatory columns not added, dont see purpose why this exist for other than main menu key
    },
    'Item Modifiers': {
        'sortOrder': 7
    },
    'Modifier': {
        'id': 7,
        'posDisplayName': 7,
        'multiSelect': 7,
        'isNested': 7,
        'isOptional': 7,
        'priceType': 7,
        'canGuestSelectMoreModifiers': 7,
        'minSelector': 7,
        'maxSelector': 7,
        'isSizeModifier': 7,
        #'showOnPos': 7,
        #'showOnKiosk': 7,
        #'showOnMpos': 7,
        #'showOnQR': 7,
        #'showOnline': 7,
        #'showOnThirdParty': 7,
        'limitIndividualModifierSelection': 7

        # additional madatory columns not added, dont see purpose why this exist for other than main menu key
    },
    'Modifier Option': {
        'id': 7,
        'posDisplayName': 7,
        #'kdsDisplayName': 7,
        'price': 7,
        'isStockAvailable': 7,
        'isSizeModifier': 7
    },
    'Modifier ModifierOptions': {
        'isDefaultSelected': 7,
        'maxLimit': 7
    },
    'Modifier Group': {
        'onPrem': 7,
        'offPrem': 7,
        'posDisplayname': 7
    },
    'Setting': {},
    'Visibility Setting': {},
    'Day Schedule': {},
    'Category ModifierGroups': {
        'sortOrder': 7   
    },
    'Category Modifiers': {
        'sortOrder': 7   
    },
    'Allergen': {},
    'Tag': {},
    'Item Modifier Group': {
        'sortOrder': 7   
    }
}

def truncate_values(df, column_name, max_length=16):
    return df[column_name].apply(lambda x: x[:max_length] if isinstance(x, str) else x)

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
        data['posDisplayName'] = data['menuName']
        #data['menuDescription'] = data['menuName']
        data['posButtonColor'] = ["#e34032"] * len(data)
        data['sortOrder'] = list(range(1, len(data) + 1))
        #data['restaurantId'] = [1] * len(data)
    dataframes[sheetname] = data

def fix_category_sheet(dataframes, filename, sheetname):
    data = read_or_create_sheet(filename, sheet_name=sheetname)
    data['categoryName'] = remove_quotations(data['categoryName'])
    category_names = data['categoryName'].tolist()
    data['id'] = list(range(1, len(data) + 1))
    data['posDisplayName'] = category_names
    data['posDisplayName'] = remove_quotations(data['posDisplayName'])
    data['posDisplayName'] = truncate_values(data, 'posDisplayName')

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

    data['id'] = list(range(1, len(data) + 1))
    data['itemName'] = remove_quotations(data['itemName'])
    data['posDisplayName'] = data['itemName']
    data['posDisplayName'] = truncate_values(data, 'posDisplayName')
    data['kdsName'] = data['itemName']
    #data['showOnMenu'] = ["TRUE"] * len(data)
    #data['showOnline'] = ["TRUE"] * len(data)
    #data['showPOS'] = ["TRUE"] * len(data)
    #data['showQR'] = ["TRUE"] * len(data)
    #data['showThirdParty'] = ["TRUE"] * len(data)
    data['orderQuantityLimit'] = ["TRUE"] * len(data)
    data['minLimit'] = [1] * len(data)
    data['maxLimit'] = [999] * len(data)

    # newer additions
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
    data['posDisplayName'] = data['optionName']
    data['posDisplayName'] = truncate_values(data, 'posDisplayName')
    #data['kdsDisplayName'] = data['optionName']
    if 'price' not in data.columns or not pd.to_numeric(data['price'], errors='coerce').notnull().all():
        data['price'] = [0] * len(data)
    data['isStockAvailable'] = ["TRUE"] * len(data)
    data['isSizeModifier'] = ["FALSE"] * len(data)
    dataframes[sheetname] = data

def fix_modifier_modifier_options(dataframes, filename, sheetname):
    data = read_or_create_sheet(filename, sheet_name=sheetname)
    data['isDefaultSelected'] = ["FALSE"] * len(data)
    data['maxLimit'] = [1] * len(data)

    # NEWLY ADDED ONE
    data2 = filename["Modifier"]
    data3 = filename["Modifier Option"]

    data = data.merge(data2[['id', 'modifierName', 'isNested']], left_on='modifierId', right_on='id', how='left', suffixes=('', '_data2'))
    data = data.merge(data3[['id', 'optionName']], left_on='modifierOptionId', right_on='id', how='left', suffixes=('', '_data3'))
    
    data['optionDisplayName'] = data.apply(lambda row: f"{row['optionName']} {row['modifierName']}" if row['isNested'] == "TRUE" else row['optionName'], axis=1)
    data.drop(columns=['id', 'id_data3', 'modifierName', 'isNested', 'optionName'], inplace=True)

    dataframes[sheetname] = data

def fix_modifier_group(dataframes, filename, sheetname):
    data = read_or_create_sheet(filename, sheet_name=sheetname)
    data['onPrem'] = ["TRUE"] * len(data)
    data['offPrem'] = ["TRUE"] * len(data)
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
    data['posDisplayName'] = data['modifierName']
    data['posDisplayName'] = truncate_values(data, 'posDisplayName')

    data['multiSelect'] = ["FALSE"] * len(data)
    data['isNested'] = ["FALSE"] * len(data)

    data['isOptional'] = data['isOptional'].apply(lambda x: "TRUE" if x != False else "FALSE")
    #data['priceType'] = ["individual"] * len(data)
    #data['canGuestSelectMoreModifiers'] = ["TRUE"] * len(data)
    #data['minSelector'] = [0] * len(data)
    data['isSizeModifier'] = ["FALSE"] * len(data)

    #data['showOnPos'] = ["TRUE"] * len(data)
    #data['showOnKiosk'] = ["TRUE"] * len(data)
    #data['showOnMpos'] = ["TRUE"] * len(data)
    #data['showOnQR'] = ["TRUE"] * len(data)
    #data['showOnline'] = ["TRUE"] * len(data)
    #data['showOnThirdParty'] = ["TRUE"] * len(data)
    data['limitIndividualModifierSelection'] = ["TRUE"] * len(data)

    df2 = filename["Modifier ModifierOptions"]
    modifier_counts = df2.groupby('modifierId').size().reset_index(name='count')
    data = data.merge(modifier_counts, left_on='id', right_on='modifierId', how='left')
    data['maxSelector'] = data['count'].fillna(0)
    data.drop(['count', 'modifierId'], axis=1, inplace=True)

    data['maxSelector'] = data.apply(lambda row: 1 if row['isOptional'] == "FALSE" else row['maxSelector'], axis=1)

    # NEW additions
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
    for sheetname in missing_fields.keys():
        if sheetname == "Menu":
            fix_menu_sheet(dataframes, filename, sheetname)

        elif sheetname == "Category":
            fix_category_sheet(dataframes, filename, sheetname)

        elif sheetname == "Category Items":
            fix_category_items_sheet(dataframes, filename, sheetname)

        elif sheetname == "Item":
            fix_items_sheet(dataframes, filename, sheetname)

        elif sheetname == "Item Modifiers":
            fix_item_modifiers(dataframes, filename, sheetname)

        elif sheetname == "Modifier":
            fix_modifier(dataframes, filename, sheetname)

        elif sheetname == "Modifier ModifierOptions":
            fix_modifier_modifier_options(dataframes, filename, sheetname)

        elif sheetname == "Modifier Option":
            fix_modifier_options(dataframes, filename, sheetname)
        
        # NO DATA
        elif sheetname == "Modifier Group":
            fix_modifier_group(dataframes, filename, sheetname)

        # NO DATA
        elif sheetname == "Category Modifiers":
            fix_category_modifiers(dataframes, filename, sheetname)

        # NO DATA
        elif sheetname == "Category ModifierGroups":
            fix_category_modifier_group(dataframes, filename, sheetname)

        # NO DATA
        elif sheetname == "Item Modifier Group":
            fix_item_modifier_group(dataframes, filename, sheetname)

        elif sheetname == "Tag":
            fix_tags(dataframes, sheetname)

        elif sheetname == "Allergen":
            fix_allergen(dataframes, sheetname)

        else:
            add_remaining(dataframes, filename, sheetname)

    # tag and allergens should be called here
    logger.info("Filling in missing fields has been completed.")

    return dataframes