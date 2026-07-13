from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.dna import router as dna_router
from app.api.v1.twin import router as twin_router
from app.api.v1.coach import router as coach_router
from app.api.v1.transactions import router as txn_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(dna_router, prefix="/dna", tags=["Financial DNA"])
api_router.include_router(twin_router, prefix="/twin", tags=["Living Financial Twin"])
api_router.include_router(coach_router, prefix="/coach", tags=["AI Coach"])
api_router.include_router(txn_router, prefix="/transactions", tags=["Transactions"])
