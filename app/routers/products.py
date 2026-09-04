from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import (
    create_product,
    get_products,
    get_product,
    update_product,
    delete_product,
)
from app.database import get_session
from app.schemas import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductFilter,
    PaginationParams,
)

router = APIRouter(prefix="/api/products", tags=["products"])


@router.get("", response_model=dict)
async def list_products(
    page: int = 1,
    per_page: int = 20,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    category_id: Optional[int] = None,
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    session: AsyncSession = Depends(get_session),
):
    pagination = PaginationParams(page=page, per_page=per_page)
    filters = ProductFilter(
        min_price=min_price,
        max_price=max_price,
        category_id=category_id,
        search=search,
        is_active=is_active,
    )
    products, total = await get_products(session, pagination, filters)
    return {
        "items": [ProductResponse.model_validate(p) for p in products],
        "total": total,
        "page": page,
        "per_page": per_page,
    }


@router.post("", response_model=ProductResponse, status_code=201)
async def create_product_endpoint(
    data: ProductCreate,
    session: AsyncSession = Depends(get_session),
):
    try:
        product = await create_product(session, data)
        product = await get_product(session, product.id)
        return ProductResponse.model_validate(product)
    except ValueError as e:
        if "invalid category" in str(e).lower():
            raise HTTPException(status_code=400, detail="Invalid category_id")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        if "foreign key" in str(e).lower() or "constraint" in str(e).lower():
            raise HTTPException(status_code=400, detail="Invalid category_id")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product_detail(
    product_id: int,
    session: AsyncSession = Depends(get_session),
):
    product = await get_product(session, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return ProductResponse.model_validate(product)


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product_endpoint(
    product_id: int,
    data: ProductUpdate,
    session: AsyncSession = Depends(get_session),
):
    product = await get_product(session, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    try:
        product = await update_product(session, product, data)
        return ProductResponse.model_validate(product)
    except Exception as e:
        if "foreign key" in str(e).lower() or "constraint" in str(e).lower():
            raise HTTPException(status_code=400, detail="Invalid category_id")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{product_id}", status_code=204)
async def delete_product_endpoint(
    product_id: int,
    session: AsyncSession = Depends(get_session),
):
    product = await get_product(session, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    await delete_product(session, product)
