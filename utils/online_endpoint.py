import re
import time
import aiohttp
import asyncio
import requests
import pandas as pd
from io import BytesIO

def normalize_url(input_url, platform):

    # Define a regex pattern to capture the base store URL
    if platform == 'Doordash': 
        pattern = r'^(https?://www\.doordash\.com/store/[^/]+/)'
    elif platform == 'Ubereats':  
        pattern = r'^(https?://www\.ubereats\.com/store/[^/]+/[^/?]+)'

    # Attempt to match the entire input URL
    match = re.match(pattern, input_url)
    if match:
        # If a match is found, return the captured group (base URL)
        return match.group(1)
    else:
        # If not matched, attempt to search within the URL
        search_match = re.search(pattern, input_url)
        if search_match:
            return search_match.group(1)
    
    # If no match is found, return None
    return None

async def get_data(url, data, seconds=1200):
  
    try:
        a = time.time()

        timeout = aiohttp.ClientTimeout(total=seconds)

        # simple request is blocking code, using aiohttp instead to create async session
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, json=data) as response:

                if response.status == 200:
                    raw_data = await response.json()
                    
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
                    print("Error:", response.status, await response.text())
        
        b = time.time()
        print("Total time =", b - a)

    except aiohttp.ClientError as e:
        print("An error occurred:", e)

    except Exception as e:
        print("An unexpected error occurred:", e)

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
    url = data['Url']

    return int(cat_scraped), int(total_categories), url

async def checker(queue):
    """
    runs async for providing current status of scraping
    checks status, forwards it, waits, repeat
    """
    
    try:
        while True:
            # get status
            status = check_status()

            # yield status by putting it into the queue
            await queue.put(status)

            # wait for few seconds
            await asyncio.sleep(7)

    except asyncio.CancelledError:
        # Signal to stop
        await queue.put(None)        