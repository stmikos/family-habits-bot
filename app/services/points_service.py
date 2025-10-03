# Purpose: Сервис для работы с очками и балансом детей.
# Context: Domain logic for points, coins, and ledger management.
# Requirements: Atomic operations, proper logging, balance calculations.

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core import get_logger, ChildNotFoundError
from app.db.models import Child, PointsLedger
from app.api.schemas import Balance, PointsLedger as PointsLedgerSchema

logger = get_logger(__name__)


class PointsService:
    """Сервис для работы с очками и монетами."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_balance(self, child_id: int) -> Balance:
        """
        Получить баланс ребёнка.
        
        Args:
            child_id: ID ребёнка.
            
        Returns:
            Balance: Баланс очков и монет.
            
        Raises:
            ChildNotFoundError: Если ребёнок не найден.
        """
        child = await self.session.get(Child, child_id)
        if not child or not child.is_active:
            raise ChildNotFoundError(child_id)
        
        return Balance(
            child_id=child_id,
            points=child.points,
            coins=child.coins
        )
    
    async def add_delta(
        self,
        child_id: int,
        delta_points: int = 0,
        delta_coins: int = 0,
        reason: str = "",
        ref_id: Optional[int] = None
    ) -> Balance:
        """
        Добавить/убавить очки/монеты и записать в ledger.
        
        Args:
            child_id: ID ребёнка.
            delta_points: Изменение очков (может быть отрицательным).
            delta_coins: Изменение монет (может быть отрицательным).
            reason: Причина изменения.
            ref_id: ID связанной сущности.
            
        Returns:
            Balance: Новый баланс.
            
        Raises:
            ChildNotFoundError: Если ребёнок не найден.
        """
        child = await self.session.get(Child, child_id)
        if not child or not child.is_active:
            raise ChildNotFoundError(child_id)
        
        # Обновляем баланс
        child.points += delta_points
        child.coins += delta_coins
        
        # Защита от отрицательных значений
        child.points = max(0, child.points)
        child.coins = max(0, child.coins)
        
        # Записываем в ledger
        ledger_entry = PointsLedger(
            child_id=child_id,
            delta_points=delta_points,
            delta_coins=delta_coins,
            reason=reason,
            ref_id=ref_id
        )
        
        self.session.add(ledger_entry)
        await self.session.commit()
        await self.session.refresh(child)
        
        logger.info(f"Points updated for child {child_id}: {delta_points:+d} points, {delta_coins:+d} coins. Reason: {reason}")
        
        return Balance(
            child_id=child_id,
            points=child.points,
            coins=child.coins
        )
    
    async def get_ledger(
        self,
        child_id: int,
        limit: int = 50,
        offset: int = 0
    ) -> List[PointsLedgerSchema]:
        """
        Получить историю изменений очков/монет.
        
        Args:
            child_id: ID ребёнка.
            limit: Максимальное количество записей.
            offset: Смещение для пагинации.
            
        Returns:
            List[PointsLedgerSchema]: История изменений.
        """
        query = (
            select(PointsLedger)
            .where(PointsLedger.child_id == child_id)
            .order_by(PointsLedger.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        
        result = await self.session.execute(query)
        entries = result.scalars().all()
        
        return [PointsLedgerSchema.model_validate(entry) for entry in entries]
    
    async def get_stats(self, child_id: int) -> dict:
        """
        Получить статистику по очкам/монетам за разные периоды.
        
        Args:
            child_id: ID ребёнка.
            
        Returns:
            dict: Статистика.
        """
        # Общая сумма заработанных очков/монет
        query = (
            select(
                func.coalesce(func.sum(PointsLedger.delta_points), 0).label("total_points_earned"),
                func.coalesce(func.sum(PointsLedger.delta_coins), 0).label("total_coins_earned")
            )
            .where(
                PointsLedger.child_id == child_id,
                PointsLedger.delta_points > 0  # Только положительные изменения
            )
        )
        
        result = await self.session.execute(query)
        row = result.first()
        
        # Потраченные монеты
        spent_query = (
            select(func.coalesce(func.sum(PointsLedger.delta_coins), 0))
            .where(
                PointsLedger.child_id == child_id,
                PointsLedger.delta_coins < 0,  # Только отрицательные изменения
                PointsLedger.reason.like("%purchase%")
            )
        )
        
        spent_result = await self.session.execute(spent_query)
        coins_spent = abs(spent_result.scalar() or 0)
        
        # Текущий баланс
        balance = await self.get_balance(child_id)
        
        return {
            "current_points": balance.points,
            "current_coins": balance.coins,
            "total_points_earned": row.total_points_earned if row else 0,
            "total_coins_earned": row.total_coins_earned if row else 0,
            "coins_spent": coins_spent
        }