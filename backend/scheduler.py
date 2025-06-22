from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio
import scraper

scheduler = AsyncIOScheduler()

def schedule_product_scraping(url: str, product_id: int, interval_minutes: int = 1):
    job_id = f"track_{product_id}"

    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)

    scheduler.add_job(
        lambda: asyncio.create_task(scraper.scrape_and_save(url, product_id)),
        "interval",
        minutes=interval_minutes,
        id=job_id,
        replace_existing=True
    )
