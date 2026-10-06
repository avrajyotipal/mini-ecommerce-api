from typing import List

from pydantic import BaseModel, Field


# -------------------------
# Product Schemas
# -------------------------

class ProductCreate(BaseModel):
    name: str = Field(min_length=2)
    price: float = Field(gt=0)
    stock: int = Field(ge=0)


class ProductResponse(BaseModel):
    id: int
    name: str
    price: float
    stock: int

    class Config:
        from_attributes = True


# -------------------------
# Order Schemas
# -------------------------

class OrderItemCreate(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(gt=0)


class OrderCreate(BaseModel):
    customer: str = Field(min_length=2)
    items: List[OrderItemCreate] = Field(min_length=1)


class OrderItemResponse(BaseModel):
    product_id: int
    quantity: int
    price: float

    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    id: int
    customer: str
    total_amount: float
    status: str
    items: List[OrderItemResponse]

    class Config:
        from_attributes = True


# -------------------------
# Order Status
# -------------------------

class OrderStatusUpdate(BaseModel):
    status: str