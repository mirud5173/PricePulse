from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base
from sqlalchemy.orm import relationship

class PriceAlert(Base):
    __tablename__ = "price_alerts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("tracked_products.id"))
    target_price = Column(Float)
    active = Column(Boolean, default=True)

    user = relationship("User", back_populates="alerts")
    product = relationship("TrackedProduct", back_populates="alerts")


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    alerts = relationship("PriceAlert", back_populates="user", cascade="all, delete-orphan")
    products = relationship("TrackedProduct", back_populates="user")


class TrackedProduct(Base):
    __tablename__ = "tracked_products"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    url = Column(String)
    product_name = Column(String)
    image_url = Column(String)
    last_scraped = Column(DateTime, default=datetime.utcnow)
    alerts = relationship("PriceAlert", back_populates="product", cascade="all, delete-orphan")
    user = relationship("User", back_populates="products")
    history = relationship(
        "PriceHistory",
        back_populates="product",
        cascade="all, delete-orphan"
    )


class PriceHistory(Base):
    __tablename__ = "price_history"
    id = Column(Integer, primary_key=True)
    tracked_product_id = Column(Integer, ForeignKey("tracked_products.id"))
    price = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)

    product = relationship("TrackedProduct", back_populates="history")
