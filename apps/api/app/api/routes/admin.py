from fastapi import APIRouter

router = APIRouter()


@router.get("/status")
def admin_status() -> dict[str, object]:
    return {
        "configured": False,
        "message": "Administrative authentication and live operations are not configured.",
    }
