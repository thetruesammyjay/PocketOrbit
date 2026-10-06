from fastapi import APIRouter

from app.services.source_service import list_demo_sources

router = APIRouter()


@router.get("/demo")
def demo_sources() -> dict[str, object]:
    return {"items": list_demo_sources(), "isDemo": True}
