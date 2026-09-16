from fastapi import APIRouter, Depends
from pydantic.networks import EmailStr

from app.api.deps import get_current_active_superuser
from app.models import Message
from app.services import email_client

router = APIRouter(prefix="/utils", tags=["utils"])


@router.post(
    "/test-email/",
    dependencies=[Depends(get_current_active_superuser)],
    status_code=201,
)
async def test_email(email_to: EmailStr) -> Message:
    """Send a test email via the email microservice."""
    await email_client.send_email_request(email_type="test", recipients=[str(email_to)])
    return Message(message="Test email sent")


@router.get("/health-check/")
async def health_check() -> str:
    return "Healthy"
