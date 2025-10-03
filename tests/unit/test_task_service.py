# Purpose: Тесты для TaskService - создание, выполнение, одобрение заданий.
# Context: Unit tests for domain logic validation and business rules.
# Requirements: Test happy path, edge cases, error handling, async operations.

import pytest
from app.services.task_service import TaskService
from app.db.models import TaskStatus, TaskType
from app.api.schemas import TaskCreate, CheckInCreate
from app.core.exceptions import TaskNotFoundError, ChildNotFoundError, TaskAlreadySubmittedError, DomainError
from tests.factories import FamilyFactory, ParentFactory, ChildFactory, TaskFactory


@pytest.mark.asyncio
async def test_create_task_success(session):
    """Тест успешного создания задания."""
    # Arrange
    family = FamilyFactory()
    session.add(family)
    await session.flush()
    
    parent = ParentFactory(family_id=family.id)
    child = ChildFactory(family_id=family.id)
    session.add_all([parent, child])
    await session.commit()
    
    task_service = TaskService(session)
    task_data = TaskCreate(
        title="Убрать комнату",
        description="Навести порядок в своей комнате",
        type="text",
        points=10,
        coins=5,
        child_id=child.id,
        parent_id=parent.id
    )
    
    # Act
    result = await task_service.create_task(task_data)
    
    # Assert
    assert result.title == "Убрать комнату"
    assert result.points == 10
    assert result.coins == 5
    assert result.status == TaskStatus.new
    assert result.child_id == child.id
    assert result.parent_id == parent.id


@pytest.mark.asyncio
async def test_create_task_child_not_found(session):
    """Тест создания задания для несуществующего ребёнка."""
    # Arrange
    family = FamilyFactory()
    session.add(family)
    await session.flush()
    
    parent = ParentFactory(family_id=family.id)
    session.add(parent)
    await session.commit()
    
    task_service = TaskService(session)
    task_data = TaskCreate(
        title="Test task",
        description="Test description",
        type="text",
        points=5,
        child_id=999,  # Несуществующий ребёнок
        parent_id=parent.id
    )
    
    # Act & Assert
    with pytest.raises(ChildNotFoundError):
        await task_service.create_task(task_data)


@pytest.mark.asyncio
async def test_create_task_family_mismatch(session):
    """Тест создания задания для ребёнка из другой семьи."""
    # Arrange
    family1 = FamilyFactory()
    family2 = FamilyFactory()
    session.add_all([family1, family2])
    await session.flush()
    
    parent = ParentFactory(family_id=family1.id)
    child = ChildFactory(family_id=family2.id)  # Другая семья
    session.add_all([parent, child])
    await session.commit()
    
    task_service = TaskService(session)
    task_data = TaskCreate(
        title="Test task",
        description="Test description", 
        type="text",
        points=5,
        child_id=child.id,
        parent_id=parent.id
    )
    
    # Act & Assert
    with pytest.raises(DomainError) as exc_info:
        await task_service.create_task(task_data)
    
    assert exc_info.value.code == "family_mismatch"


@pytest.mark.asyncio
async def test_submit_task_text_success(session):
    """Тест успешной сдачи текстового задания."""
    # Arrange
    family = FamilyFactory()
    session.add(family)
    await session.flush()
    
    parent = ParentFactory(family_id=family.id)
    child = ChildFactory(family_id=family.id)
    task = TaskFactory(
        parent_id=parent.id,
        child_id=child.id,
        type=TaskType.text,
        status=TaskStatus.new
    )
    session.add_all([parent, child, task])
    await session.commit()
    
    task_service = TaskService(session)
    checkin_data = CheckInCreate(
        task_id=task.id,
        child_id=child.id,
        note="Выполнил задание!"
    )
    
    # Act
    result = await task_service.submit_task(task.id, child.id, checkin_data)
    
    # Assert
    assert result.status == TaskStatus.done
    assert result.id == task.id


@pytest.mark.asyncio
async def test_submit_task_validation_error(session):
    """Тест валидации при сдаче задания неподходящего типа."""
    # Arrange
    family = FamilyFactory()
    session.add(family)
    await session.flush()
    
    parent = ParentFactory(family_id=family.id)
    child = ChildFactory(family_id=family.id)
    task = TaskFactory(
        parent_id=parent.id,
        child_id=child.id,
        type=TaskType.photo,  # Требует медиафайл
        status=TaskStatus.new
    )
    session.add_all([parent, child, task])
    await session.commit()
    
    task_service = TaskService(session)
    checkin_data = CheckInCreate(
        task_id=task.id,
        child_id=child.id,
        note="Только текст, без фото"  # Нет media_id
    )
    
    # Act & Assert
    with pytest.raises(DomainError) as exc_info:
        await task_service.submit_task(task.id, child.id, checkin_data)
    
    assert exc_info.value.code == "validation_error"


@pytest.mark.asyncio
async def test_approve_task_adds_points(session):
    """Тест начисления очков при одобрении задания."""
    # Arrange
    family = FamilyFactory()
    session.add(family)
    await session.flush()
    
    parent = ParentFactory(family_id=family.id)
    child = ChildFactory(family_id=family.id, points=0, coins=0)
    task = TaskFactory(
        parent_id=parent.id,
        child_id=child.id,
        points=7,
        coins=3,
        status=TaskStatus.done
    )
    session.add_all([parent, child, task])
    await session.commit()
    
    task_service = TaskService(session)
    
    # Act
    result = await task_service.approve_task(task.id, parent.id)
    
    # Assert
    assert result.status == TaskStatus.approved
    
    # Проверяем обновление баланса ребёнка
    await session.refresh(child)
    assert child.points == 7
    assert child.coins == 3


@pytest.mark.asyncio
async def test_approve_task_idempotent(session):
    """Тест идемпотентности одобрения задания."""
    # Arrange
    family = FamilyFactory()
    session.add(family)
    await session.flush()
    
    parent = ParentFactory(family_id=family.id)
    child = ChildFactory(family_id=family.id, points=0)
    task = TaskFactory(
        parent_id=parent.id,
        child_id=child.id,
        points=5,
        status=TaskStatus.approved  # Уже одобрено
    )
    session.add_all([parent, child, task])
    await session.commit()
    
    task_service = TaskService(session)
    
    # Act
    result = await task_service.approve_task(task.id, parent.id)
    
    # Assert
    assert result.status == TaskStatus.approved
    # Баланс не должен измениться при повторном одобрении
    await session.refresh(child)
    assert child.points == 0  # Изначальный баланс


@pytest.mark.asyncio 
async def test_reject_task_success(session):
    """Тест успешного отклонения задания."""
    # Arrange
    family = FamilyFactory()
    session.add(family)
    await session.flush()
    
    parent = ParentFactory(family_id=family.id)
    child = ChildFactory(family_id=family.id)
    task = TaskFactory(
        parent_id=parent.id,
        child_id=child.id,
        status=TaskStatus.done
    )
    session.add_all([parent, child, task])
    await session.commit()
    
    task_service = TaskService(session)
    
    # Act
    result = await task_service.reject_task(task.id, parent.id, "Плохо выполнено")
    
    # Assert
    assert result.status == TaskStatus.rejected


@pytest.mark.asyncio
async def test_get_tasks_with_filters(session):
    """Тест получения заданий с фильтрацией."""
    # Arrange
    family = FamilyFactory()
    session.add(family)
    await session.flush()
    
    parent = ParentFactory(family_id=family.id)
    child = ChildFactory(family_id=family.id)
    
    # Создаём задания разных статусов
    task1 = TaskFactory(parent_id=parent.id, child_id=child.id, status=TaskStatus.done)
    task2 = TaskFactory(parent_id=parent.id, child_id=child.id, status=TaskStatus.approved)
    task3 = TaskFactory(parent_id=parent.id, child_id=child.id, status=TaskStatus.new)  # Должно быть отфильтровано
    
    session.add_all([parent, child, task1, task2, task3])
    await session.commit()
    
    task_service = TaskService(session)
    
    # Act
    results = await task_service.get_tasks(child_id=child.id)
    
    # Assert
    assert len(results) == 2  # task3 с статусом 'new' не включено
    result_ids = {task.id for task in results}
    assert task1.id in result_ids
    assert task2.id in result_ids
    assert task3.id not in result_ids