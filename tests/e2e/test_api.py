"""E2E тесты для REST API."""

import pytest

from app.db.models import Family, Parent, Child, Task, TaskType, TaskStatus


async def create_test_parent_and_family(session, tg_id: int) -> tuple[Family, Parent]:
    """Создать тестовую семью и родителя."""
    family = Family()
    session.add(family)
    await session.flush()
    
    parent = Parent(family_id=family.id, tg_id=tg_id)
    session.add(parent)
    await session.flush()
    
    return family, parent


async def create_test_child(session, family_id: int, name: str) -> Child:
    """Создать тестового ребёнка."""
    child = Child(family_id=family_id, name=name, points=0, coins=0)
    session.add(child)
    await session.flush()
    return child


class TestAuthAPI:
    """Тесты авторизации и аутентификации."""

    def test_auth_me_creates_new_parent(self, client):
        """Тест создания нового родителя при первом входе."""
        # Act
        response = client.get(
            "/api/v1/auth/me",
            headers={"X-TG-User-ID": "12345"}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "parent"
        assert data["tg_id"] == 12345
        assert "user_id" in data
        assert "family_id" in data

    @pytest.mark.asyncio
    async def test_auth_me_returns_existing_parent(self, client, session):
        """Тест возврата существующего родителя."""
        # Arrange
        family, parent = await create_test_parent_and_family(session, 67890)
        await session.commit()

        # Act
        response = client.get(
            "/api/v1/auth/me",
            headers={"X-TG-User-ID": "67890"}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "parent"
        assert data["tg_id"] == 67890
        assert data["user_id"] == parent.id


class TestChildrenAPI:
    """Тесты управления детьми."""

    @pytest.mark.asyncio
    async def test_create_child_success(self, client, session):
        """Тест успешного создания ребёнка."""
        # Arrange
        family, parent = await create_test_parent_and_family(session, 11111)
        await session.commit()

        child_data = {
            "name": "Тест ребёнок"
        }

        # Act
        response = client.post(
            "/api/v1/children",
            headers={"X-TG-User-ID": "11111"},
            json=child_data
        )

        # Assert
        assert response.status_code == 200, f"Response: {response.text}"
        data = response.json()
        assert data["name"] == "Тест ребёнок"
        assert data["family_id"] == family.id
        assert data["points"] == 0
        assert data["coins"] == 0

    @pytest.mark.asyncio
    async def test_list_children_success(self, client, session):
        """Тест получения списка детей."""
        # Arrange
        family, parent = await create_test_parent_and_family(session, 22222)
        child1 = await create_test_child(session, family.id, "Ребёнок 1")
        child2 = await create_test_child(session, family.id, "Ребёнок 2")
        await session.commit()

        # Act
        response = client.get(
            "/api/v1/children",
            headers={"X-TG-User-ID": "22222"}
        )

        # Assert
        assert response.status_code == 200, f"Response: {response.text}"
        data = response.json()
        assert len(data) == 2
        names = [child["name"] for child in data]
        assert "Ребёнок 1" in names
        assert "Ребёнок 2" in names


class TestTasksAPI:
    """Тесты управления заданиями."""

    @pytest.mark.asyncio
    async def test_create_task_success(self, client, session):
        """Тест успешного создания задания."""
        # Arrange
        family, parent = await create_test_parent_and_family(session, 33333)
        child = await create_test_child(session, family.id, "Тест ребёнок")
        await session.commit()

        task_data = {
            "title": "Убрать комнату",
            "description": "Убрать игрушки и заправить кровать",
            "type": "text",
            "points": 5,
            "coins": 2,
            "child_id": child.id
        }

        # Act
        response = client.post(
            "/api/v1/tasks",
            headers={"X-TG-User-ID": "33333"},
            json=task_data
        )

        # Assert
        assert response.status_code == 200, f"Response: {response.text}"
        data = response.json()
        assert data["title"] == "Убрать комнату"
        assert data["type"] == "text"
        assert data["status"] == "new"
        assert data["child_id"] == child.id
        assert data["parent_id"] == parent.id

    @pytest.mark.asyncio
    async def test_list_tasks_empty(self, client, session):
        """Тест получения пустого списка заданий."""
        # Arrange
        family, parent = await create_test_parent_and_family(session, 44444)
        child = await create_test_child(session, family.id, "Тест ребёнок")
        await session.commit()

        # Act
        response = client.get(
            "/api/v1/tasks",
            headers={"X-TG-User-ID": "44444"}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data == []


class TestTaskFlow:
    """Тесты полного цикла работы с заданиями."""

    @pytest.mark.asyncio
    async def test_full_task_workflow(self, client, session):
        """Тест полного workflow: создание → сдача → одобрение."""
        # Arrange
        family, parent = await create_test_parent_and_family(session, 55555)
        child = await create_test_child(session, family.id, "Тест ребёнок")
        await session.commit()

        # Step 1: Создание задания
        task_data = {
            "title": "Помыть посуду",
            "description": "Помыть всю посуду после ужина",
            "type": "photo",
            "points": 10,
            "coins": 5,
            "child_id": child.id
        }

        response = client.post(
            "/api/v1/tasks",
            headers={"X-TG-User-ID": "55555"},
            json=task_data
        )

        assert response.status_code == 200, f"Response: {response.text}"
        task = response.json()
        task_id = task["id"]

        # Step 2: Сдача задания
        checkin_data = {
            "task_id": task_id,
            "note": "Посуда помыта!",
            "media_id": "photo123"
        }

        response = client.post(
            "/api/v1/checkins",
            headers={"X-TG-User-ID": "55555"},
            json=checkin_data
        )

        assert response.status_code == 200, f"Response: {response.text}"
        checkin = response.json()
        assert checkin["note"] == "Посуда помыта!"

        # Step 3: Одобрение задания
        response = client.post(
            f"/api/v1/tasks/{task_id}/approve",
            headers={"X-TG-User-ID": "55555"}
        )

        assert response.status_code == 200, f"Response: {response.text}"
        approved_task = response.json()
        assert approved_task["status"] == "approved"

        # Step 4: Проверка баланса ребёнка
        response = client.get(
            "/api/v1/points/balance",
            headers={"X-TG-User-ID": "55555"},
            params={"child_id": child.id}
        )

        assert response.status_code == 200, f"Response: {response.text}"
        balance = response.json()
        assert balance["points"] == 10
        assert balance["coins"] == 5