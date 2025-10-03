# Purpose: Points and balance endpoints.
# Context: Get child balance, points ledger, stats.
# Requirements: /points/balance endpoint.

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.session import get_session
from app.api.schemas import UserInfo, Balance, PointsLedgerEntry
from app.api.routes.auth import get_current_user
from app.services.points_service import PointsService
from app.core import get_logger

router = APIRouter(prefix="/points", tags=["points"])
logger = get_logger(__name__)


@router.get("/balance", response_model=Balance)
async def get_balance(
    child_id: int = None,
    session: AsyncSession = Depends(get_session),
    current_user: UserInfo = Depends(get_current_user)
) -> Balance:
    """Получить баланс очков и монет."""
    # Определяем, чей баланс запрашивается
    if current_user.role == "child":
        # Ребёнок может получить только свой баланс
        target_child_id = current_user.user_id
    else:
        # Родитель может запросить баланс любого своего ребёнка
        if not child_id:
            raise HTTPException(status_code=400, detail="child_id is required for parents")
        
        # TODO: Проверить, что ребёнок принадлежит этому родителю
        target_child_id = child_id
    
    points_service = PointsService(session)
    balance = await points_service.get_balance(target_child_id)
    
    return balance


@router.get("/ledger", response_model=List[PointsLedgerEntry])
async def get_ledger(
    child_id: int = None,
    limit: int = 50,
    session: AsyncSession = Depends(get_session),
    current_user: UserInfo = Depends(get_current_user)
) -> List[PointsLedgerEntry]:
    """Получить историю начислений очков."""
    # Определяем, чью историю запрашивается
    if current_user.role == "child":
        target_child_id = current_user.user_id
    else:
        if not child_id:
            raise HTTPException(status_code=400, detail="child_id is required for parents")
        target_child_id = child_id
    
    points_service = PointsService(session)
    ledger = await points_service.get_ledger(target_child_id, limit=limit)
    
    return ledger