from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import (
    create_category,
    get_categories,
    get_category,
    update_category,
    delete_category,
)
from app.database import get_session
from app.models import Product
from app.schemas import CategoryCreate, CategoryUpdate, CategoryResponse, PaginationParams

router = APIRouter(prefix="/api/categories", tags=["categories"])


@router.get("", response_model=dict)
async def list_categories(
    page: int = 1,
    per_page: int = 20,
    session: AsyncSession = Depends(get_session),
):
    pagination = PaginationParams(page=page, per_page=per_page)
    categories, total = await get_categories(session, pagination)
    return {
        "items": [CategoryResponse.model_validate(c) for c in categories],
        "total": total,
        "page": page,
        "per_page": per_page,
    }


@router.post("", response_model=CategoryResponse, status_code=201)
async def create_category_endpoint(
    data: CategoryCreate,
    session: AsyncSession = Depends(get_session),
):
    try:
        category = await create_category(session, data)
        return CategoryResponse.model_validate(category)
    except Exception as e:
        if "unique" in str(e).lower() or "duplicate" in str(e).lower():
            raise HTTPException(status_code=400, detail="Category with this name already exists")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category_detail(
    category_id: int,
    session: AsyncSession = Depends(get_session),
):
    category = await get_category(session, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return CategoryResponse.model_validate(category)


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category_endpoint(
    category_id: int,
    data: CategoryUpdate,
    session: AsyncSession = Depends(get_session),
):
    category = await get_category(session, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    try:
        category = await update_category(session, category, data)
        return CategoryResponse.model_validate(category)
    except Exception as e:
        if "unique" in str(e).lower() or "duplicate" in str(e).lower():
            raise HTTPException(status_code=400, detail="Category with this name already exists")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{category_id}", status_code=204)
async def delete_category_endpoint(
    category_id: int,
    session: AsyncSession = Depends(get_session),
):
    category = await get_category(session, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    product_count = (
        await session.execute(
            select(func.count()).select_from(Product).where(Product.category_id == category_id)
        )
    ).scalar_one()
    if product_count > 0:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete category with associated products",
        )
    try:
        await delete_category(session, category)
    except Exception as e:
        if "foreign key" in str(e).lower() or "constraint" in str(e).lower():
            raise HTTPException(
                status_code=400,
                detail="Cannot delete category with associated products",
            )
        raise HTTPException(status_code=500, detail=str(e))
