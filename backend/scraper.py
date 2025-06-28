from playwright.async_api import async_playwright
from sqlalchemy.orm import Session
from datetime import datetime
import models
import database
from email_utils import send_email_if_needed


async def scrape_and_save(url: str, product_id: int):
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
        )
        
        context = await browser.new_context(user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/113.0.0.0 Safari/537.36"
        ))
        page = await context.new_page()

        try:
            print(f"[→] Scraping product ID {product_id}: {url}")
            await page.goto(url, timeout=60000, wait_until='domcontentloaded')
            await page.wait_for_selector("span#productTitle", timeout=15000)
            title = await page.locator("span#productTitle").inner_text()

            try:
                price_text = await page.locator("span.a-price > span.a-offscreen").first.inner_text()
            except:
                price_text = "Not Available"

            try:
                image_url = await page.locator("img#landingImage").get_attribute("src")
            except:
                image_url = ""

            # Clean price
            try:
                price = float(price_text.replace("₹", "").replace(",", "").strip())
            except:
                price = None

            # 🔧 MANUAL OVERRIDE FOR ALERT TESTING
            if product_id == 8: 
                price = 270.0  
                print(f"[!] Manually overridden price for testing: ₹{price}")

            print(f"[✓] {title.strip()} — ₹{price}" if price else "[!] Price not available")

            # Save to DB
            db: Session = next(database.get_db())
            product = db.query(models.TrackedProduct).filter(models.TrackedProduct.id == product_id).first()
            if product:
                product.product_name = title.strip()
                product.image_url = image_url
                product.last_scraped = datetime.utcnow()

                if price is not None:
                    new_entry = models.PriceHistory(
                        tracked_product_id=product_id,
                        price=price,
                        timestamp=datetime.utcnow()
                    )
                    db.add(new_entry)

                db.commit()

            await send_email_if_needed(product_id, price, db)

            return {
                "title": title.strip(),
                "price": price,
                "image_url": image_url
            }

        except Exception as e:
            print(f"[✗] Error scraping {url}: {e}")
            return {"error": str(e)}

        finally:
            await browser.close()
