from fastapi import APIRouter

from app.api.v1.block import router as block_router
from app.api.v1.car import router as car_router
from app.api.v1.firmware import router as firmware_router
from app.api.v1.link import router as link_router
from app.api.v1.version import router as version_router

router = APIRouter(prefix="/api/v1")

router.include_router(firmware_router)
router.include_router(version_router)
router.include_router(block_router)
router.include_router(car_router)
router.include_router(link_router)
