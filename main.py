from typing import List

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

import models
import schemas

from database import engine, get_db
from exceptions import (
    product_not_found,
    insufficient_stock,
    invalid_status,
    order_not_found,
    invalid_status_transition
)


# Create database tables
models.Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Mini E-Commerce API",
    description="FastAPI backend for products and orders",
    version="1.0.0"
)


# =========================================================
# PRODUCT APIs
# =========================================================

@app.post(
    "/products",
    response_model=schemas.ProductResponse,
    status_code=201
)
def create_product(
    product: schemas.ProductCreate,
    db: Session = Depends(get_db)
):

    new_product = models.Product(
        name=product.name,
        price=product.price,
        stock=product.stock
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return new_product


@app.get(
    "/products",
    response_model=List[schemas.ProductResponse]
)
def get_products(
    db: Session = Depends(get_db)
):

    products = db.query(models.Product).all()

    return products


# =========================================================
# ORDER APIs
# =========================================================

@app.post(
    "/orders",
    response_model=schemas.OrderResponse,
    status_code=201
)
def create_order(
    order: schemas.OrderCreate,
    db: Session = Depends(get_db)
):

    total_amount = 0

    order_items = []

    # -----------------------------------------
    # Validate products and calculate total
    # -----------------------------------------

    for item in order.items:

        product = db.query(models.Product).filter(
            models.Product.id == item.product_id
        ).first()

        # Product doesn't exist
        if not product:
            raise product_not_found()

        # Check stock
        if item.quantity > product.stock:
            raise insufficient_stock()

        # Server-side calculation
        item_total = product.price * item.quantity

        total_amount += item_total

        order_item = models.OrderItem(
            product_id=product.id,
            quantity=item.quantity,
            price=product.price
        )

        order_items.append(order_item)

    # -----------------------------------------
    # Create order
    # -----------------------------------------

    new_order = models.Order(
        customer=order.customer,
        total_amount=total_amount,
        status="PLACED"
    )

    db.add(new_order)
    db.flush()

    # -----------------------------------------
    # Add order items + reduce stock
    # -----------------------------------------

    for item in order_items:

        item.order_id = new_order.id

        db.add(item)

        product = db.query(models.Product).filter(
            models.Product.id == item.product_id
        ).first()

        product.stock -= item.quantity

    db.commit()

    db.refresh(new_order)

    return new_order


@app.get(
    "/orders",
    response_model=List[schemas.OrderResponse]
)
def get_orders(
    db: Session = Depends(get_db)
):

    orders = (
        db.query(models.Order)
        .options(
            joinedload(models.Order.items)
        )
        .all()
    )

    return orders


@app.get(
    "/orders/{order_id}",
    response_model=schemas.OrderResponse
)
def get_order(
    order_id: int,
    db: Session = Depends(get_db)
):

    order = (
        db.query(models.Order)
        .options(
            joinedload(models.Order.items)
        )
        .filter(models.Order.id == order_id)
        .first()
    )

    if not order:
        raise order_not_found()

    return order


# =========================================================
# ORDER STATUS API
# =========================================================

@app.put(
    "/orders/{order_id}/status",
    response_model=schemas.OrderResponse
)
def update_order_status(
    order_id: int,
    status_update: schemas.OrderStatusUpdate,
    db: Session = Depends(get_db)
):

    order = db.query(models.Order).filter(
        models.Order.id == order_id
    ).first()

    if not order:
        raise order_not_found()

    new_status = status_update.status.upper()

    valid_statuses = [
        "PLACED",
        "PROCESSING",
        "SHIPPED",
        "DELIVERED"
    ]

    if new_status not in valid_statuses:
        raise invalid_status()

    # -----------------------------------------
    # Status transition validation
    # -----------------------------------------

    allowed_transitions = {
        "PLACED": "PROCESSING",
        "PROCESSING": "SHIPPED",
        "SHIPPED": "DELIVERED"
    }

    if order.status != "DELIVERED":

        expected_next_status = allowed_transitions.get(
            order.status
        )

        if new_status != expected_next_status:
            raise invalid_status_transition()

    else:
        raise invalid_status_transition()

    order.status = new_status

    db.commit()
    db.refresh(order)

    return order