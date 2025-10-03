# Purpose: Shop service for managing shop items and purchases.
# Context: Handles shop item listing, purchase transactions, inventory management.
# Requirements: Validate coin balance, atomic transactions, log purchases in PointsLedger.

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from datetime import datetime

from app.db.models import ShopItem, Purchase, Child, PointsLedger
from app.core import get_logger
from app.core.exceptions import NotFoundError, ValidationError

logger = get_logger(__name__)


class ShopService:
    """Service for shop operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def list_active_items(self) -> List[ShopItem]:
        """
        Получить список активных товаров в магазине.
        
        Returns:
            List[ShopItem]: Список активных товаров
        """
        result = await self.session.execute(
            select(ShopItem)
            .where(ShopItem.is_active == True)
            .order_by(ShopItem.price_coins)
        )
        items = result.scalars().all()
        logger.info(f"Listed {len(items)} active shop items")
        return list(items)
    
    async def get_item_by_id(self, item_id: int) -> ShopItem:
        """
        Получить товар по ID.
        
        Args:
            item_id: ID товара
            
        Returns:
            ShopItem: Найденный товар
            
        Raises:
            NotFoundError: Если товар не найден
        """
        result = await self.session.execute(
            select(ShopItem).where(ShopItem.id == item_id)
        )
        item = result.scalar_one_or_none()
        
        if not item:
            raise NotFoundError(
                code="shop_item_not_found",
                message=f"Shop item with id={item_id} not found"
            )
        
        return item
    
    async def purchase_item(self, child_id: int, item_id: int) -> Purchase:
        """
        Купить товар за монеты.
        
        Args:
            child_id: ID ребёнка
            item_id: ID товара
            
        Returns:
            Purchase: Запись о покупке
            
        Raises:
            NotFoundError: Если товар или ребёнок не найден
            ValidationError: Если недостаточно монет или товар неактивен
        """
        # Получаем ребёнка
        child_result = await self.session.execute(
            select(Child).where(Child.id == child_id)
        )
        child = child_result.scalar_one_or_none()
        
        if not child:
            raise NotFoundError(
                code="child_not_found",
                message=f"Child with id={child_id} not found"
            )
        
        # Получаем товар
        item = await self.get_item_by_id(item_id)
        
        if not item.is_active:
            raise ValidationError(
                code="item_not_available",
                message="This item is no longer available"
            )
        
        # Проверяем баланс
        if child.coins < item.price_coins:
            raise ValidationError(
                code="insufficient_coins",
                message=f"Insufficient coins. Required: {item.price_coins}, available: {child.coins}"
            )
        
        # Списываем монеты
        child.coins -= item.price_coins
        
        # Создаём запись о покупке
        purchase = Purchase(
            child_id=child_id,
            item_id=item_id,
            cost_coins=item.price_coins
        )
        self.session.add(purchase)
        
        # Записываем в ledger
        ledger_entry = PointsLedger(
            child_id=child_id,
            delta_points=0,
            delta_coins=-item.price_coins,
            reason="shop_purchase",
            ref_id=item_id
        )
        self.session.add(ledger_entry)
        
        await self.session.commit()
        await self.session.refresh(purchase)
        
        logger.info(
            f"Child {child_id} purchased item {item_id} ({item.title}) "
            f"for {item.price_coins} coins"
        )
        
        return purchase
    
    async def get_child_purchases(self, child_id: int) -> List[Purchase]:
        """
        Получить историю покупок ребёнка.
        
        Args:
            child_id: ID ребёнка
            
        Returns:
            List[Purchase]: Список покупок
        """
        result = await self.session.execute(
            select(Purchase)
            .where(Purchase.child_id == child_id)
            .order_by(Purchase.created_at.desc())
        )
        purchases = result.scalars().all()
        
        logger.info(f"Retrieved {len(purchases)} purchases for child {child_id}")
        return list(purchases)
