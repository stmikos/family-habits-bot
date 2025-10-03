# Purpose: Unit tests for TaskService with simplified factory approach.
# Context: Test domain logic for task management.
# Requirements: Use build() instead of create() to avoid session issues.

import pytest
from unittest.mock import AsyncMock, patch
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Task, TaskStatus, TaskType, CheckIn, Child
from app.services.task_service import TaskService
from app.services.points_service import PointsService
from app.core.exceptions import DomainError

from tests.factories import FamilyFactory, ParentFactory, ChildFactory, TaskFactory


@pytest.mark.asyncio
async def test_create_task_success(session: AsyncSession):
    """Тест успешного создания задания."""
    # Arrange
    family = FamilyFactory()
    session.add(family)
    await session.flush()

    parent = ParentFactory(family_id=family.id)
    child = ChildFactory(family_id=family.id)
    session.add_all([parent, child])
    await session.commit()

    from app.api.schemas import TaskCreate
    
    task_service = TaskService(session)
    task_data = TaskCreate(
        title="Убрать комнату",
        description="Убрать игрушки и заправить кровать",
        type="text",
        points=5,
        coins=2,
        parent_id=parent.id,
        child_id=child.id
    )

    # Act
    result = await task_service.create_task(task_data)

    # Assert
    assert result.title == "Убрать комнату"
    assert result.type == TaskType.text
    assert result.status == TaskStatus.new
    assert result.parent_id == parent.id
    assert result.child_id == child.id


@pytest.mark.asyncio
async def test_submit_task_success(session: AsyncSession):
    """Тест успешной сдачи задания."""
    # Arrange
    family = FamilyFactory()
    session.add(family)
    await session.flush()

    parent = ParentFactory(family_id=family.id)
    child = ChildFactory(family_id=family.id)
    session.add_all([parent, child])
    await session.flush()

    # Создаём задание через билд
    task = TaskFactory.build(
        parent_id=parent.id,
        child_id=child.id,
        type=TaskType.text,
        status=TaskStatus.new
    )
    session.add(task)
    await session.commit()

    from app.api.schemas import CheckInCreate
    
    task_service = TaskService(session)
    payload = CheckInCreate(
        task_id=task.id,
        child_id=child.id,
        note="Задание выполнено!"
    )

    # Act
    result = await task_service.submit_task(task.id, child.id, payload)

    # Assert
    assert result.status == TaskStatus.done
    
    # Проверяем CheckIn
    check_ins = await session.execute(
        select(CheckIn).where(CheckIn.task_id == task.id)
    )
    check_in = check_ins.scalar_one()
    assert check_in.note == "Задание выполнено!"


@pytest.mark.asyncio
async def test_approve_task_success(session: AsyncSession):
    """Тест успешного одобрения задания."""
    # Arrange
    family = FamilyFactory()
    session.add(family)
    await session.flush()

    parent = ParentFactory(family_id=family.id)
    child = ChildFactory(family_id=family.id, points=0, coins=0)
    session.add_all([parent, child])
    await session.flush()

    task = TaskFactory.build(
        parent_id=parent.id,
        child_id=child.id,
        points=7,
        coins=3,
        status=TaskStatus.done
    )
    session.add(task)
    await session.commit()

    task_service = TaskService(session)

    # Act
    result = await task_service.approve_task(task.id, parent.id)

    # Assert
    assert result.status == TaskStatus.approved
    
    # Проверяем, что очки начислены ребёнку
    await session.refresh(child)
    assert child.points == 7
    assert child.coins == 3


@pytest.mark.asyncio
async def test_reject_task_success(session: AsyncSession):
    """Тест успешного отклонения задания."""
    # Arrange
    family = FamilyFactory()
    session.add(family)
    await session.flush()

    parent = ParentFactory(family_id=family.id)
    child = ChildFactory(family_id=family.id)
    session.add_all([parent, child])
    await session.flush()

    task = TaskFactory.build(
        parent_id=parent.id,
        child_id=child.id,
        status=TaskStatus.done
    )
    session.add(task)
    await session.commit()

    task_service = TaskService(session)

    # Act
    result = await task_service.reject_task(task.id, parent.id, "Плохо выполнено")

    # Assert
    assert result.status == TaskStatus.rejected