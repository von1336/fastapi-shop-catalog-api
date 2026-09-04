from typing import Optional

from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Category, Product
from app.schemas import (
    CategoryCreate,
    CategoryUpdate,
    ProductCreate,
    ProductUpdate,
    ProductFilter,
    PaginationParams,
)


async def create_category(session: AsyncSession, data: CategoryCreate) -> Category:
    category = Category(**data.model_dump())
    session.add(category)
    await session.flush()
    await session.refresh(category)
    return category


async def get_categories(
    session: AsyncSession,
    pagination: PaginationParams,
) -> tuple[list[Category], int]:
    count_query = select(func.count()).select_from(Category)
    total = (await session.execute(count_query)).scalar_one()

    query = select(Category).offset((pagination.page - 1) * pagination.per_page).limit(pagination.per_page)
    result = await session.execute(query)
    categories = result.scalars().all()
    return list(categories), total


async def get_category(session: AsyncSession, category_id: int) -> Optional[Category]:
    result = await session.execute(select(Category).where(Category.id == category_id))
    return result.scalar_one_or_none()


async def update_category(session: AsyncSession, category: Category, data: CategoryUpdate) -> Category:
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(category, field, value)
    await session.flush()
    await session.refresh(category)
    return category


async def delete_category(session: AsyncSession, category: Category) -> None:
    await session.delete(category)
    await session.flush()


async def create_product(session: AsyncSession, data: ProductCreate) -> Product:
    category = await get_category(session, data.category_id)
    if not category:
        raise ValueError("Invalid category_id")
    product = Product(**data.model_dump())
    session.add(product)
    await session.flush()
    await session.refresh(product)
    return product


def _apply_product_filters(query, filters: Optional[ProductFilter] = None):
    if filters:
        if filters.min_price is not None:
            query = query.where(Product.price >= filters.min_price)
        if filters.max_price is not None:
            query = query.where(Product.price <= filters.max_price)
        if filters.category_id is not None:
            query = query.where(Product.category_id == filters.category_id)
        if filters.search:
            search_term = f"%{filters.search}%"
            query = query.where(
                or_(
                    Product.name.ilike(search_term),
                    Product.description.ilike(search_term),
                )
            )
        if filters.is_active is not None:
            query = query.where(Product.is_active == filters.is_active)
    return query


async def get_products(
    session: AsyncSession,
    pagination: PaginationParams,
    filters: Optional[ProductFilter] = None,
) -> tuple[list[Product], int]:
    count_query = select(func.count()).select_from(Product)
    count_query = _apply_product_filters(count_query, filters)
    total = (await session.execute(count_query)).scalar_one()

    query = select(Product).options(selectinload(Product.category))
    query = _apply_product_filters(query, filters)
    query = query.offset((pagination.page - 1) * pagination.per_page).limit(pagination.per_page)
    result = await session.execute(query)
    products = result.scalars().all()
    return list(products), total


async def get_product(session: AsyncSession, product_id: int) -> Optional[Product]:
    result = await session.execute(
        select(Product)
        .options(selectinload(Product.category))
        .where(Product.id == product_id)
    )
    return result.scalar_one_or_none()


async def get_products_by_category(
    session: AsyncSession,
    category_id: int,
    pagination: PaginationParams,
) -> tuple[list[Product], int]:
    filters = ProductFilter(category_id=category_id)
    return await get_products(session, pagination, filters)


async def update_product(session: AsyncSession, product: Product, data: ProductUpdate) -> Product:
    update_data = data.model_dump(exclude_unset=True)
    if "category_id" in update_data:
        category = await get_category(session, update_data["category_id"])
        if not category:
            raise ValueError("Invalid category_id")
    for field, value in update_data.items():
        setattr(product, field, value)
    await session.flush()
    await session.refresh(product)
    return product


async def delete_product(session: AsyncSession, product: Product) -> None:
    await session.delete(product)
    await session.flush()
