from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models
import schemas
import auth
import database

router = APIRouter()

@router.post("/alerts", response_model=schemas.AlertResponse)
def create_alert(alert: schemas.AlertCreate, db: Session = Depends(database.get_db), user=Depends(auth.get_current_user)):
    product = db.query(models.TrackedProduct).filter_by(id=alert.product_id, user_id=user.id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    new_alert = models.PriceAlert(user_id=user.id, product_id=alert.product_id, target_price=alert.target_price)
    db.add(new_alert)
    db.commit()
    db.refresh(new_alert)
    return new_alert
