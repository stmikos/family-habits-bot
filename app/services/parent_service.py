# Purpose: Parent service layer for Family Habit Bot.
# Context: Business logic для работы с родителями.
# Requirements: Создание родителей, получение детей, создание семьи.

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.models import Parent, Child, Family, Plan
from app.core import get_logger

logger = get_logger(__name__)


class ParentService:
    """Сервис для работы с родителями."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_parent_by_tg_id(self, tg_id: int) -> Optional[Parent]:
        """Получить родителя по Telegram ID."""
        result = await self.session.execute(
            select(Parent).where(Parent.tg_id == tg_id)
        )
        return result.scalar_one_or_none()

    async def create_parent(self, tg_id: int, name: Optional[str] = None) -> Parent:
        """Создать нового родителя с семьёй."""
        # Создаём семью
        family = Family(plan=Plan.FREE)
        self.session.add(family)
        await self.session.flush()  # Получаем ID семьи

        # Создаём родителя
        parent = Parent(
            tg_id=tg_id,
            name=name,
            family_id=family.id
        )
        self.session.add(parent)
        await self.session.commit()
        await self.session.refresh(parent)

        logger.info(f"Created parent {parent.id} with family {family.id}")
        return parent

    async def get_children(self, parent_id: int) -> List[Child]:
        """Получить всех детей родителя."""
        # Сначала получаем родителя
        parent = await self.session.get(Parent, parent_id)
        if not parent:
            return []

        # Получаем детей из той же семьи
        result = await self.session.execute(
            select(Child).where(
                Child.family_id == parent.family_id,
                Child.is_active == True
            )
        )
        return list(result.scalars().all())

    async def add_child_to_family(self, parent_id: int, child_name: str) -> Child:
        """Добавить ребёнка в семью родителя."""
        parent = await self.session.get(Parent, parent_id)
        if not parent:
            raise ValueError("Parent not found")

        child = Child(
            name=child_name,
            family_id=parent.family_id
        )
        self.session.add(child)
        await self.session.commit()
        await self.session.refresh(child)

        logger.info(f"Added child {child.id} to family {parent.family_id}")
        return child

    async def get_family_stats(self, parent_id: int) -> dict:
        """Получить статистику семьи."""
        parent = await self.session.get(Parent, parent_id)
        if not parent:
            return {}

        # Получаем детей
        children = await self.get_children(parent_id)
        
        # Получаем общую статистику
        from sqlalchemy import func
        from app.db.models import Task

        tasks_count = await self.session.scalar(
            select(func.count(Task.id)).where(Task.parent_id == parent_id)
        )

        total_points = sum(child.points for child in children)
        total_coins = sum(child.coins for child in children)

        return {
            "children_count": len(children),
            "tasks_created": tasks_count or 0,
            "total_points": total_points,
            "total_coins": total_coins,
            "children": [
                {
                    "id": child.id,
                    "name": child.name,
                    "points": child.points,
                    "coins": child.coins,
                    "has_telegram": child.tg_id is not None
                }
                for child in children
            ]
        }