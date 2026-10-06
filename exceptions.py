from fastapi import HTTPException


def product_not_found():
    return HTTPException(
        status_code=404,
        detail="Product not found"
    )


def insufficient_stock():
    return HTTPException(
        status_code=400,
        detail="Insufficient product stock"
    )


def invalid_status():
    return HTTPException(
        status_code=400,
        detail="Invalid order status"
    )


def order_not_found():
    return HTTPException(
        status_code=404,
        detail="Order not found"
    )


def invalid_status_transition():
    return HTTPException(
        status_code=400,
        detail="Invalid order status transition"
    )