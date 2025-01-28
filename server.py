import time
import uvicorn  
import requests
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from utils.logging_config import setup_logger
from competitor.online.online_to_aio import process_online_only
from utils.online_endpoint import get_data, normalize_url, check_status
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

logger = setup_logger(__name__)

is_processing = False

# FastAPI application
app = FastAPI()

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Request model
class ScrapeRequest(BaseModel):
    platform: str
    input_url: str

@app.get("/health")
async def health_check():
    return {"status": "OK"}

@app.post("/scrapingcancelation")
async def cancel():
    url = "http://54.218.231.251:8000/cancel-scraping"
    data = requests.post(url)

    if data.status_code == 200:
        logger.info("Scraping terminated successfully.")
        return {"status": "Canceled Successfully"}
    else:
        logger.info("Scraping termination unsuccessful.")
        return {"status": "Cancelation Unsuccessful"}

@app.get("/checkstatus")
async def status():
    scraped, total, _ = check_status()

    if total == 0:
        return {"progress": 1}
    else:
        return {"progress": round((scraped / total) * 100)} 

@app.post("/menupreonboarding")
def scrape_menu(request: ScrapeRequest):

    # multi-request handling disabled
    global is_processing
    if is_processing:
        raise HTTPException(status_code=429, detail="Another request is being processed. Please wait.")
    is_processing = True

    platform = request.platform
    input_url = request.input_url
    try:
        # normalize input url
        normalized_input_url = normalize_url(input_url, platform)
        if normalized_input_url is None:
            raise HTTPException(status_code=403, detail=f"Invalid {platform} URL format.")
        logger.info(f"Scraping of {normalized_input_url} has started.")

        # prepare data and make scraping API request
        start = time.time()

        api_url = "http://54.218.231.251:8000/menu-onboarding-scraper"
        request_data = { "link": normalized_input_url, "platform": platform }
        file, empty = get_data(api_url, request_data)

        end = time.time()

        if empty:
            raise HTTPException(status_code=422, detail="Empty dataframe recieved from scraping endpoint.")
        logger.info(f"File recieved from scraping endpoint in {round((end - start)/60, 2)} minutes.")

        # convert to aio format
        result_data, name = process_online_only(file, platform)
        logger.info("Online to AIO format conversion completed. File returned successfully.")

        filename = f"{name}-{platform}.xlsx"
        return StreamingResponse(
            result_data,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error.")
    
    finally:
        is_processing = False
    
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8040)