from fastapi import APIRouter, Depends
from pydantic import BaseModel
import logging
import scraper
import auth  # Adjust the import paths if needed

# Set up logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

router = APIRouter()

class ScrapeRequest(BaseModel):
    url: str
    product_id: int

@router.post("/scrape")
async def scrape_product(req: ScrapeRequest, user=Depends(auth.get_current_user)):
    logger.info(f"Scraping URL: {req.url} for product ID: {req.product_id}")
    result = await scraper.scrape_and_save(req.url, req.product_id)
    return result
