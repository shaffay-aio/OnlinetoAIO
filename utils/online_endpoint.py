import time
import requests
import pandas as pd
from io import BytesIO

def fun_request(url, data):

    try:
        a = time.time()
        response = requests.post(url, json=data)

        if response.status_code == 200:
            #print("Response:", response.json())

            raw_data = response.json()
    
            data = raw_data['data']
            info_data = data['info']
            items_data = data['items']
            modifier_data = data['modifiers']

            info_df = pd.DataFrame(info_data)
            items_df = pd.DataFrame(items_data)
            modifier_df = pd.DataFrame(modifier_data)

            file_path = fun_save_to_excel(info_df, items_df, modifier_df)
            return file_path

        else:
            print("Error:", response.status_code, response.text)

        b = time.time()
        print("total time = ", b - a)

    except requests.exceptions.RequestException as e:
        print("An error occurred:", e)

def fun_save_to_excel(info_df, items_df, modifier_df):
    # Create a BytesIO object to hold the Excel data in memory
    excel_buffer = BytesIO()

    # Use ExcelWriter to write data to the BytesIO object
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        info_df.to_excel(writer, sheet_name="info", index=False)
        items_df.to_excel(writer, sheet_name="items", index=False)
        modifier_df.to_excel(writer, sheet_name="modifiers", index=False)

    # Ensure the buffer is ready to be read from the beginning
    excel_buffer.seek(0)

    print("Data has been saved to an Excel object in memory.")
    return excel_buffer

def check_status():

    url = "http://54.218.231.251:8000/check-status"
    response = requests.post(url)
    data = response.json()['data']

    last_update = data['Last Updated']
    platform = data['Platform']
    total_categories = data['Total Categories']
    cat_now = data['Category Now']
    cat_scraped = data['Categories Scraped']

    return f'{cat_scraped}/{total_categories}'