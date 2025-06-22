from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from urllib.parse import quote

import models
import schemas
import auth
import scraper
import database
from scheduler import scheduler, schedule_product_scraping

router = APIRouter()


@router.post("/add_product")
async def add_product(
    data: schemas.AddProductRequest,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # 🔒 Check for duplicate product for the user
    existing = db.query(models.TrackedProduct).filter_by(user_id=current_user.id, url=str(data.url)).first()
    if existing:
        raise HTTPException(status_code=400, detail="You're already tracking this product.")

    # Step 1: Insert placeholder product
    new_product = models.TrackedProduct(
        url=str(data.url),
        user_id=current_user.id,
        product_name="Scraping...",
        image_url=""
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    # Step 2: Scrape and update product data
    try:
        result = await scraper.scrape_and_save(url=str(data.url), product_id=new_product.id)

        if "error" in result:
            db.delete(new_product)
            db.commit()
            raise HTTPException(status_code=400, detail="Scraping failed: " + result["error"])

        # ✅ Schedule scraping every 1 minute (for testing)
        schedule_product_scraping(str(data.url), new_product.id, interval_minutes=1)

        return {"message": "Product added successfully", "id": new_product.id}
    except Exception as e:
        db.delete(new_product)
        db.commit()
        raise HTTPException(status_code=500, detail="Unexpected error during scraping: " + str(e))


@router.get("/my_products", response_model=list[schemas.ProductResponse])
def get_my_products(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    products = db.query(models.TrackedProduct).filter_by(user_id=current_user.id).all()
    return products


@router.delete("/delete_product/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    try:
        product = db.query(models.TrackedProduct).filter_by(id=product_id, user_id=current_user.id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        db.delete(product)
        db.commit()

        try:
            scheduler.remove_job(f"track_{product_id}")
        except Exception:
            pass

        return {"message": "Product deleted successfully"}
    except Exception as e:
        print(f"❌ Error deleting product {product_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

