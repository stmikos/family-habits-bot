# Purpose: Определить минимальные модели для Task, CheckIn, Child, Parent, PointsLedger.
# Context: SQLAlchemy models for Family Habit domain entities.
# Requirements: явные типы, индексы, внешние ключи, soft-delete через is_active.

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey, DateTime, Enum, Boolean, Text, func
from datetime import datetime
import enum


class Base(DeclarativeBase):
    """Базовый класс для всех моделей."""
    pass


class TaskType(str, enum.Enum):
    """Тип задания."""
    text = "text"
    photo = "photo" 
    video = "video"


class TaskStatus(str, enum.Enum):
    """Статус задания."""
    new = "new"
    in_progress = "in_progress"
    done = "done"
    approved = "approved"
    rejected = "rejected"


class Plan(str, enum.Enum):
    """Тарифный план семьи."""
    FREE = "free"
    PRO = "pro"


class Family(Base):
    """Семья - группа родителей и детей."""
    __tablename__ = "families"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    plan: Mapped[Plan] = mapped_column(Enum(Plan), default=Plan.FREE, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Relationships
    parents: Mapped[list["Parent"]] = relationship("Parent", back_populates="family")
    children: Mapped[list["Child"]] = relationship("Child", back_populates="family")


class Parent(Base):
    """Родитель - создаёт задания и проверяет выполнение."""
    __tablename__ = "parents"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    family_id: Mapped[int] = mapped_column(ForeignKey("families.id", ondelete="CASCADE"), index=True)
    tg_id: Mapped[int] = mapped_column(index=True, unique=True)
    name: Mapped[str] = mapped_column(String(64), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    
    # Relationships
    family: Mapped["Family"] = relationship("Family", back_populates="parents")
    tasks: Mapped[list["Task"]] = relationship("Task", back_populates="parent")


class Child(Base):
    """Ребёнок - выполняет задания и получает очки."""
    __tablename__ = "children"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    family_id: Mapped[int] = mapped_column(ForeignKey("families.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(64))
    points: Mapped[int] = mapped_column(Integer, default=0)
    coins: Mapped[int] = mapped_column(Integer, default=0)
    avatar: Mapped[str] = mapped_column(String(32), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    
    # Relationships
    family: Mapped["Family"] = relationship("Family", back_populates="children")
    tasks: Mapped[list["Task"]] = relationship("Task", back_populates="child")
    checkins: Mapped[list["CheckIn"]] = relationship("CheckIn", back_populates="child")
    ledger_entries: Mapped[list["PointsLedger"]] = relationship("PointsLedger", back_populates="child")


class Task(Base):
    """Задание от родителя для ребёнка."""
    __tablename__ = "tasks"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    parent_id: Mapped[int] = mapped_column(ForeignKey("parents.id", ondelete="CASCADE"), index=True)
    child_id: Mapped[int] = mapped_column(ForeignKey("children.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(120))
    description: Mapped[str] = mapped_column(Text)
    type: Mapped[TaskType] = mapped_column(Enum(TaskType))
    points: Mapped[int] = mapped_column(Integer, default=5)
    coins: Mapped[int] = mapped_column(Integer, default=0)
    due_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[TaskStatus] = mapped_column(Enum(TaskStatus), default=TaskStatus.new, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    parent: Mapped["Parent"] = relationship("Parent", back_populates="tasks")
    child: Mapped["Child"] = relationship("Child", back_populates="tasks")
    checkins: Mapped[list["CheckIn"]] = relationship("CheckIn", back_populates="task")


class CheckIn(Base):
    """Отметка выполнения задания ребёнком."""
    __tablename__ = "checkins"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id", ondelete="CASCADE"), index=True)
    child_id: Mapped[int] = mapped_column(ForeignKey("children.id", ondelete="CASCADE"), index=True)
    note: Mapped[str | None] = mapped_column(String(280), nullable=True)
    media_id: Mapped[str | None] = mapped_column(String(128), nullable=True)  # file_id из TG
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    
    # Relationships
    task: Mapped["Task"] = relationship("Task", back_populates="checkins")
    child: Mapped["Child"] = relationship("Child", back_populates="checkins")


class PointsLedger(Base):
    """Журнал начислений/списаний очков и монет."""
    __tablename__ = "points_ledger"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    child_id: Mapped[int] = mapped_column(ForeignKey("children.id", ondelete="CASCADE"), index=True)
    delta_points: Mapped[int] = mapped_column(Integer, default=0)
    delta_coins: Mapped[int] = mapped_column(Integer, default=0)
    reason: Mapped[str] = mapped_column(String(120))  # "task_approved", "shop_purchase", etc.
    ref_id: Mapped[int | None] = mapped_column(Integer, nullable=True)  # ID связанной сущности
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    
    # Relationships
    child: Mapped["Child"] = relationship("Child", back_populates="ledger_entries")


class ShopItem(Base):
    """Товар в магазине."""
    __tablename__ = "shop_items"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    sku: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(120))
    description: Mapped[str] = mapped_column(Text, nullable=True)
    price_coins: Mapped[int] = mapped_column(Integer)
    image_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Purchase(Base):
    """Покупка товара ребёнком."""
    __tablename__ = "purchases"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    child_id: Mapped[int] = mapped_column(ForeignKey("children.id", ondelete="CASCADE"), index=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("shop_items.id", ondelete="CASCADE"))
    cost_coins: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    
    # Relationships
    child: Mapped["Child"] = relationship("Child")
    item: Mapped["ShopItem"] = relationship("ShopItem")


class RewardRule(Base):
    """Правило начисления наград за достижения."""
    __tablename__ = "reward_rules"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(120))
    threshold_points: Mapped[int] = mapped_column(Integer)
    reward_type: Mapped[str] = mapped_column(String(32))  # "badge", "coins", "item"
    payload: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON with reward details
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())