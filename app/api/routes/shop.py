# Purpose: API endpoints for shop operations.
# Context: REST API for listing items, purchasing, viewing inventory.
# Requirements: Validate auth, handle errors, return proper status codes.

from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.api.schemas import ShopItemResponse, PurchaseCreate, PurchaseResponse
from app.db.session import get_session
from app.services.shop_service import ShopService
from app.core.exceptions import NotFoundError, ValidationError
from app.core import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/shop", tags=["shop"])


@router.get("/items", response_model=List[ShopItemResponse])
async def list_shop_items(
    session: AsyncSession = Depends(get_session)
):
    """
    Получить список активных товаров в магазине.
    """
    service = ShopService(session)
    items = await service.list_active_items()
    return items


@router.post("/purchase", response_model=PurchaseResponse, status_code=201)
async def purchase_item(
    purchase_data: PurchaseCreate,
    session: AsyncSession = Depends(get_session)
):
    """
    Купить товар за монеты.
    
    Args:
        purchase_data: Данные о покупке (child_id, item_id)
    
    Returns:
        Purchase: Информация о покупке
        
    Raises:
        404: Товар или ребёнок не найден
        400: Недостаточно монет или товар неактивен
    """
    service = ShopService(session)
    
    try:
        purchase = await service.purchase_item(
            child_id=purchase_data.child_id,
            item_id=purchase_data.item_id
        )
        
        logger.info(
            f"Purchase created: child_id={purchase_data.child_id}, "
            f"item_id={purchase_data.item_id}"
        )
        
        return purchase
        
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/inventory/{child_id}", response_model=List[PurchaseResponse])
async def get_inventory(
    child_id: int,
    session: AsyncSession = Depends(get_session)
):
    """
    Получить историю покупок ребёнка (инвентарь).
    
    Args:
        child_id: ID ребёнка
        
    Returns:
        List[Purchase]: Список покупок
    """
    service = ShopService(session)
    purchases = await service.get_child_purchases(child_id)
    
    logger.info(f"Retrieved inventory for child {child_id}")
    return purchases
