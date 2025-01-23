import time
import uvicorn  
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from utils.logging_config import setup_logger
from competitor.online.online_to_aio import process_online_only
from utils.online_endpoint import get_data, normalize_url
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

logger = setup_logger(__name__)

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

@app.post("/menupreonboarding")
async def scrape_menu(platform: str, input_url: str):

    error_detail = "Internal Server Error."
    try:
        # normalize input url
        normalized_input_url = normalize_url(input_url, platform)
        if normalized_input_url is None:
            error_detail = f"Invalid {platform} URL format."
            raise HTTPException(status_code=403, detail=f"Invalid {platform} URL format.")
        logger.info(f"Scraping of {normalized_input_url} has started.")

        # prepare data and make scraping API request
        start = time.time()

        api_url = "http://54.218.231.251:8000/menu-onboarding-scraper"
        request_data = { "link": normalized_input_url, "platform": platform }
        file, empty = get_data(api_url, request_data)

        end = time.time()

        if empty:
            error_detail = "Empty dataframe recieved from scraping endpoint."
            raise HTTPException(status_code=422, detail="Empty dataframe recieved from scraping endpoint.")
        logger.info(f"File recieved from scraping endpoint in {round(end - start, 2)} minutes.")

        # convert to aio format
        result_data, name = process_online_only(file, platform)
        logger.info("Online to AIO format conversion completed. File returned successfully.")

        return StreamingResponse(
            result_data,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={name}.xlsx"}
        )

    except Exception as e:
        logger.info(f"Exception has occured. {e}")
        raise HTTPException(status_code=500, detail=error_detail)
    
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8040)
