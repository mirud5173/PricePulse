from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import models
import auth
import database
from datetime import timedelta

router = APIRouter()

@router.get("/history/{product_id}")
def price_history(product_id: int, db: Session = Depends(database.get_db), user=Depends(auth.get_current_user)):
    product = db.query(models.TrackedProduct).filter_by(id=product_id, user_id=user.id).first()
    if not product:
        return {"error": "Product not found"}

    history = db.query(models.PriceHistory).filter_by(tracked_product_id=product.id).order_by(models.PriceHistory.timestamp).all()

    # IST offset
    ist_offset = timedelta(hours=5, minutes=30)

    return [
        {
            "timestamp": (h.timestamp + ist_offset).strftime("%Y-%m-%d %H:%M:%S"),
            "price": h.price
        }
        for h in history
    ]
