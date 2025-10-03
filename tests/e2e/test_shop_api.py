# Purpose: E2E tests for shop API endpoints.
# Context: Test shop item listing, purchasing, and inventory retrieval.
# Requirements: Test happy path and error scenarios, validate balances.

import pytest
from fastapi.testclient import TestClient

from app.db.models import ShopItem, Child, Parent, Family, Task, TaskType, TaskStatus, CheckIn


async def create_test_shop_item(session, sku: str, title: str, price: int, is_active: bool = True) -> ShopItem:
    """Создать тестовый товар в магазине."""
    item = ShopItem(
        sku=sku,
        title=title,
        description=f"Test description for {title}",
        price_coins=price,
        is_active=is_active
    )
    session.add(item)
    await session.flush()
    return item


async def create_test_family_and_child(session, child_name: str, coins: int, points: int = 0) -> tuple[Family, Child]:
    """Создать тестовую семью и ребёнка."""
    family = Family()
    session.add(family)
    await session.flush()
    
    child = Child(
        family_id=family.id,
        name=child_name,
        coins=coins,
        points=points
    )
    session.add(child)
    await session.flush()
    
    return family, child


class TestShopAPI:
    """E2E tests for shop endpoints."""
    
    def test_list_shop_items_empty(self, client: TestClient):
        """Тест: список товаров пуст, если нет активных товаров."""
        response = client.get("/api/v1/shop/items")
        
        assert response.status_code == 200
        items = response.json()
        assert isinstance(items, list)
    
    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_list_shop_items_with_data(self, client: TestClient, session):
        """Тест: список товаров возвращает активные товары."""
        # Создаём тестовые товары
        item1 = await create_test_shop_item(session, "test-item-1", "Test Item 1", 10)
        item2 = await create_test_shop_item(session, "test-item-2", "Test Item 2", 20)
        item3 = await create_test_shop_item(session, "test-item-3", "Inactive Item", 30, is_active=False)
        
        await session.commit()
        
        response = client.get("/api/v1/shop/items")
        
        assert response.status_code == 200
        items = response.json()
        assert len(items) == 2
        assert items[0]["sku"] == "test-item-1"
        assert items[1]["sku"] == "test-item-2"
    
    @pytest.mark.asyncio
    async def test_purchase_item_success(self, client: TestClient, session):
        """Тест: успешная покупка товара."""
        # Создаём семью и ребёнка
        family, child = await create_test_family_and_child(session, "Test Child", coins=50)
        
        # Создаём товар
        item = await create_test_shop_item(session, "test-purchase", "Test Purchase Item", 20)
        await session.commit()
        
        # Покупаем товар
        response = client.post(
            "/api/v1/shop/purchase",
            json={"child_id": child.id, "item_id": item.id}
        )
        
        assert response.status_code == 201
        purchase = response.json()
        assert purchase["child_id"] == child.id
        assert purchase["item_id"] == item.id
        assert purchase["cost_coins"] == 20
        
        # Проверяем, что баланс уменьшился
        await session.refresh(child)
        assert child.coins == 30
    
    @pytest.mark.asyncio
    async def test_purchase_item_insufficient_coins(self, client: TestClient, session):
        """Тест: покупка с недостаточным количеством монет."""
        # Создаём семью и ребёнка с малым балансом
        family, child = await create_test_family_and_child(session, "Poor Child", coins=5)
        
        # Создаём дорогой товар
        item = await create_test_shop_item(session, "expensive", "Expensive Item", 100)
        await session.commit()
        
        # Пытаемся купить
        response = client.post(
            "/api/v1/shop/purchase",
            json={"child_id": child.id, "item_id": item.id}
        )
        
        assert response.status_code == 400
        error = response.json()
        assert "Insufficient coins" in error["detail"]
    
    @pytest.mark.asyncio
    async def test_purchase_item_not_found(self, client: TestClient, session):
        """Тест: покупка несуществующего товара."""
        # Создаём семью и ребёнка
        family, child = await create_test_family_and_child(session, "Test Child", coins=100)
        await session.commit()
        
        # Пытаемся купить несуществующий товар
        response = client.post(
            "/api/v1/shop/purchase",
            json={"child_id": child.id, "item_id": 99999}
        )
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_get_inventory_empty(self, client: TestClient, session):
        """Тест: инвентарь пуст для нового ребёнка."""
        # Создаём семью и ребёнка
        family, child = await create_test_family_and_child(session, "Test Child", coins=0)
        await session.commit()
        
        response = client.get(f"/api/v1/shop/inventory/{child.id}")
        
        assert response.status_code == 200
        inventory = response.json()
        assert isinstance(inventory, list)
        assert len(inventory) == 0
    
    @pytest.mark.asyncio
    async def test_get_inventory_with_purchases(self, client: TestClient, session):
        """Тест: инвентарь содержит историю покупок."""
        # Создаём семью и ребёнка
        family, child = await create_test_family_and_child(session, "Test Child", coins=100)
        
        # Создаём товары
        item1 = await create_test_shop_item(session, "item-1", "Item 1", 10)
        item2 = await create_test_shop_item(session, "item-2", "Item 2", 20)
        await session.commit()
        
        # Покупаем товары
        client.post(
            "/api/v1/shop/purchase",
            json={"child_id": child.id, "item_id": item1.id}
        )
        client.post(
            "/api/v1/shop/purchase",
            json={"child_id": child.id, "item_id": item2.id}
        )
        
        # Проверяем инвентарь
        response = client.get(f"/api/v1/shop/inventory/{child.id}")
        
        assert response.status_code == 200
        inventory = response.json()
        assert len(inventory) == 2
        # Проверяем, что обе покупки присутствуют
        costs = [p["cost_coins"] for p in inventory]
        assert 10 in costs
        assert 20 in costs


class TestShopWorkflow:
    """E2E тест полного цикла: задание -> одобрение -> покупка."""
    
    @pytest.mark.asyncio
    async def test_full_shop_workflow(self, client: TestClient, session):
        """Тест: полный цикл от выполнения задания до покупки товара."""
        # 1. Создаём семью, родителя и ребёнка
        family = Family()
        session.add(family)
        await session.flush()
        
        parent = Parent(tg_id=12345, family_id=family.id, name="Test Parent")
        session.add(parent)
        await session.flush()
        
        child = Child(
            name="Test Child",
            family_id=family.id,
            coins=0,
            points=0
        )
        session.add(child)
        await session.flush()
        
        # 2. Создаём товар в магазине
        item = await create_test_shop_item(session, "reward-toy", "Reward Toy", 25)
        
        # 3. Создаём задание с монетами
        task = Task(
            parent_id=parent.id,
            child_id=child.id,
            title="Clean room",
            description="Clean your room thoroughly",
            type=TaskType.text,
            points=10,
            coins=30,
            status=TaskStatus.new
        )
        session.add(task)
        await session.flush()
        
        # 4. Ребёнок сдаёт задание
        checkin = CheckIn(
            task_id=task.id,
            child_id=child.id,
            note="Done!"
        )
        session.add(checkin)
        task.status = TaskStatus.done
        await session.flush()
        
        # 5. Родитель одобряет задание (используем сервис)
        from app.services.task_service import TaskService
        task_service = TaskService(session)
        await task_service.approve_task(task.id, parent.id)
        
        await session.refresh(child)
        assert child.coins == 30
        assert child.points == 10
        
        await session.commit()
        
        # 6. Ребёнок покупает товар
        response = client.post(
            "/api/v1/shop/purchase",
            json={"child_id": child.id, "item_id": item.id}
        )
        
        assert response.status_code == 201
        
        # 7. Проверяем баланс
        await session.refresh(child)
        assert child.coins == 5  # 30 - 25
        
        # 8. Проверяем инвентарь
        response = client.get(f"/api/v1/shop/inventory/{child.id}")
        inventory = response.json()
        assert len(inventory) == 1
        assert inventory[0]["item"]["title"] == "Reward Toy"
