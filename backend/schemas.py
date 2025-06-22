from pydantic import BaseModel, HttpUrl
from typing import Optional


class AddProductRequest(BaseModel):
    url: str


class ProductResponse(BaseModel):
    id: int
    url: str
    product_name: str
    image_url: Optional[str]

    class Config:
        from_attributes = True  # replaces deprecated `orm_mode` in Pydantic v2


class AlertCreate(BaseModel):
    product_id: int
    target_price: float
    

class AlertResponse(BaseModel):
    id: int
    product_id: int
    target_price: float
    active: bool

    class Config:
        orm_mode = True