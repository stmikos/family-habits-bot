# Purpose: Pydantic схемы для FastAPI endpoints.
# Context: DTO objects for request/response validation and serialization.
# Requirements: Clear field validation, proper typing, API documentation.

from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import List, Optional, Literal
from enum import Enum


# Base class for all schemas
class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# Auth schemas
class UserInfo(BaseModel):
    role: Literal["parent", "child"]
    user_id: int
    tg_id: int
    family_id: int


# Enums
class TaskTypeEnum(str, Enum):
    text = "text"
    photo = "photo"
    video = "video"


class TaskStatusEnum(str, Enum):
    new = "new"
    in_progress = "in_progress"
    done = "done"
    approved = "approved"
    rejected = "rejected"


class PlanEnum(str, Enum):
    FREE = "free"
    PRO = "pro"


# Family schemas
class FamilyBase(BaseSchema):
    plan: PlanEnum = PlanEnum.FREE


class FamilyCreate(FamilyBase):
    pass


class Family(FamilyBase):
    id: int
    created_at: datetime
    is_active: bool


# Parent schemas
class ParentBase(BaseSchema):
    name: Optional[str] = None


class ParentCreate(ParentBase):
    tg_id: int
    family_id: int


class Parent(ParentBase):
    id: int
    tg_id: int
    family_id: int
    is_active: bool
    created_at: datetime


# Child schemas
class ChildBase(BaseSchema):
    name: str = Field(min_length=1, max_length=64)
    avatar: Optional[str] = None


class ChildCreate(ChildBase):
    pass  # family_id берётся из current_user


class ChildUpdate(BaseSchema):
    name: Optional[str] = Field(None, min_length=1, max_length=64)
    avatar: Optional[str] = None


class Child(ChildBase):
    id: int
    family_id: int
    points: int
    coins: int
    is_active: bool
    created_at: datetime


# Task schemas
class TaskBase(BaseSchema):
    title: str = Field(min_length=3, max_length=120)
    description: str
    type: TaskTypeEnum
    points: int = Field(ge=1, le=100, default=5)
    coins: int = Field(ge=0, le=100, default=0)
    due_at: Optional[datetime] = None


class TaskCreate(TaskBase):
    child_id: int
    # parent_id устанавливается автоматически из current_user


class TaskUpdate(BaseSchema):
    title: Optional[str] = Field(None, min_length=3, max_length=120)
    description: Optional[str] = None
    type: Optional[TaskTypeEnum] = None
    points: Optional[int] = Field(None, ge=1, le=100)
    coins: Optional[int] = Field(None, ge=0, le=100)
    due_at: Optional[datetime] = None


class Task(TaskBase):
    id: int
    parent_id: int
    child_id: int
    status: TaskStatusEnum
    created_at: datetime
    updated_at: datetime


# CheckIn schemas
class CheckInBase(BaseSchema):
    note: Optional[str] = Field(None, max_length=280)
    media_id: Optional[str] = Field(None, max_length=128)


class CheckInCreate(CheckInBase):
    task_id: int
    # child_id определяется из задачи


class CheckIn(CheckInBase):
    id: int
    task_id: int
    child_id: int
    created_at: datetime


# Points Ledger schemas
class PointsLedgerBase(BaseSchema):
    delta_points: int = 0
    delta_coins: int = 0
    reason: str = Field(max_length=120)
    ref_id: Optional[int] = None


class PointsLedgerCreate(PointsLedgerBase):
    child_id: int


class PointsLedger(PointsLedgerBase):
    id: int
    child_id: int
    created_at: datetime


# Shop schemas
class ShopItemBase(BaseSchema):
    sku: str = Field(max_length=32)
    title: str = Field(max_length=120)
    description: Optional[str] = None
    price_coins: int = Field(ge=1)
    image_url: Optional[str] = Field(None, max_length=255)


class ShopItemCreate(ShopItemBase):
    pass


class ShopItem(ShopItemBase):
    id: int
    is_active: bool
    created_at: datetime


# Purchase schemas
class PurchaseCreate(BaseSchema):
    child_id: int
    item_id: int


class Purchase(BaseSchema):
    id: int
    child_id: int
    item_id: int
    cost_coins: int
    created_at: datetime
    item: ShopItem


# Balance schemas
class Balance(BaseSchema):
    child_id: int
    points: int
    coins: int


class PointsLedgerEntry(BaseSchema):
    id: int
    child_id: int
    delta_points: int
    delta_coins: int
    reason: str
    ref_id: Optional[int] = None
    created_at: datetime


# Auth schemas
class AuthUser(BaseSchema):
    role: Literal["parent", "child"]
    user_id: int
    family_id: int
    tg_id: int


# API Response schemas
class SuccessResponse(BaseSchema):
    status: str = "success"
    message: Optional[str] = None


class ErrorResponse(BaseSchema):
    status: str = "error"
    code: str
    message: str
    details: Optional[dict] = None


# Task operations
class TaskApproveRequest(BaseSchema):
    parent_id: int


class TaskRejectRequest(BaseSchema):
    parent_id: int
    reason: Optional[str] = Field(None, max_length=280)