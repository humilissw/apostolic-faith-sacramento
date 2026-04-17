from datetime import timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import CurrentUser, SessionDep, get_current_active_superuser
from app.core import security
from app.config import settings
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db_session
from app.core.security import verify_password
from app.models import Message, NewPassword, Token, UserPublic
from app.repositories.user_repo import UserRepository
from app.services.auth_service import AuthService

router = APIRouter(tags=["login"])

@router.post("/login/access-token")
async def login_access_token(
    *, form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: AsyncSession = Depends(get_db_session)
) -> Token:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    repository = UserRepository(session=session)
    user = await repository.get_by_email(email=form_data.username)
    if user is None:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return Token(
        access_token=security.create_access_token(
            user.email, expires_delta=access_token_expires
        )
    )


@router.post("/login/idp")
def logout(current_user: CurrentUser) -> Any:
    return 0;    

@router.post("/login/clear")
def logout(current_user: CurrentUser) -> Any:
    return 0;    

@router.post("/login/test-token", response_model=UserPublic)
def test_token(current_user: CurrentUser) -> Any:
    """
    Test access token
    """
    return current_user


@router.post("/password-recovery/{email}")
async def recover_password(email: str, session: SessionDep) -> Message:
    """
    Password Recovery
    """
    repository = UserRepository(session=session)
    auth_service = AuthService(user_repository=repository)

    # Use the service to initiate password recovery
    # The service handles the case where user doesn't exist gracefully
    await auth_service.initiate_password_recovery(email=email)

    return Message(message="Password recovery email sent")


@router.post("/reset-password/")
async def reset_password(session: SessionDep, body: NewPassword) -> Message:
    """
    Reset password
    """
    # Create user repository and service
    user_repository = UserRepository(session=session)
    auth_service = AuthService(user_repository=user_repository)

    # Use the service to reset the password
    result = await auth_service.reset_password(
        token=body.token,
        new_password=body.new_password,
        session=session
    )

    # Return the success message
    return Message(message=result["message"])


@router.post(
    "/password-recovery-html-content/{email}",
    dependencies=[Depends(get_current_active_superuser)],
    response_class=HTMLResponse,
)
async def recover_password_html_content(email: str, session: SessionDep) -> Any:
    """
    HTML Content for Password Recovery
    """
    # Create user repository and service
    user_repository = UserRepository(session=session)
    auth_service = AuthService(user_repository=user_repository)

    # Use the service to initiate password recovery
    await auth_service.initiate_password_recovery(email=email)

    # Return HTML content
    return HTMLResponse(
        content="Password recovery email sent successfully",
        headers={"subject:": "Password Recovery"}
    )
