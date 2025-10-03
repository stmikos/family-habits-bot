# Purpose: Factory classes for creating test data.
# Context: Test data generation using factory-boy for consistent test setup.
# Requirements: Create realistic test data, handle relationships, support async.

import factory
from factory import fuzzy
from datetime import datetime, timedelta
from app.db.models import Family, Parent, Child, Task, CheckIn, PointsLedger, TaskType, TaskStatus, Plan


class FamilyFactory(factory.Factory):
    """Factory для создания семей."""
    
    class Meta:
        model = Family
    
    plan = Plan.FREE
    is_active = True
    created_at = factory.LazyFunction(datetime.utcnow)


class ParentFactory(factory.Factory):
    """Factory для создания родителей."""
    
    class Meta:
        model = Parent
    
    family_id = None  # Должно быть установлено явно
    tg_id = factory.Sequence(lambda n: 100000 + n)
    name = factory.Faker("name")
    is_active = True
    created_at = factory.LazyFunction(datetime.utcnow)


class ChildFactory(factory.Factory):
    """Factory для создания детей."""
    
    class Meta:
        model = Child
    
    family_id = None  # Должно быть установлено явно
    name = factory.Faker("first_name")
    points = 0
    coins = 0
    avatar = None
    is_active = True
    created_at = factory.LazyFunction(datetime.utcnow)


class TaskFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Фабрика для Task."""
    
    class Meta:
        model = Task
        sqlalchemy_session_persistence = "flush"
    
    title = factory.Faker("sentence", nb_words=3, locale="en_US")
    description = factory.Faker("text", max_nb_chars=200, locale="en_US")
    type = fuzzy.FuzzyChoice(["text", "photo", "video"])
    points = 5
    coins = 0
    due_at = factory.LazyFunction(lambda: datetime.utcnow() + timedelta(days=1))
    status = TaskStatus.new
    created_at = factory.LazyFunction(datetime.utcnow)
    updated_at = factory.LazyFunction(datetime.utcnow)


class CheckInFactory(factory.Factory):
    """Factory для создания check-in."""
    
    class Meta:
        model = CheckIn
    
    task_id = None    # Должно быть установлено явно
    child_id = None   # Должно быть установлено явно
    note = factory.Faker("text", max_nb_chars=100)
    media_id = None
    created_at = factory.LazyFunction(datetime.utcnow)


class PointsLedgerFactory(factory.Factory):
    """Factory для создания записей ledger."""
    
    class Meta:
        model = PointsLedger
    
    child_id = None   # Должно быть установлено явно
    delta_points = 5
    delta_coins = 0
    reason = "task_approved"
    ref_id = None
    created_at = factory.LazyFunction(datetime.utcnow)