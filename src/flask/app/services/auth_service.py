from werkzeug.exceptions import HTTPException

from app.repositories.user_repo import UserRepository
from app.utils import (
    generate_password_reset_token,
    generate_reset_password_email,
    send_email,
    verify_password_reset_token,
)


class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repo = user_repository

    def initiate_password_recovery(self, email: str) -> None:
        user = self.user_repo.get_by_email(email=email)
        if not user:
            return
        password_reset_token = generate_password_reset_token(email=email)
        email_data = generate_reset_password_email(
            email_to=user.email, email=email, token=password_reset_token
        )
        send_email(
            email_to=user.email,
            subject=email_data.subject,
            html_content=email_data.html_content,
        )

    def reset_password(self, token: str, new_password: str, session) -> dict:
        email = verify_password_reset_token(token=token)
        if not email:
            raise HTTPException(400, "Invalid token")
        user = self.user_repo.get_by_email(email=email)
        if not user:
            raise HTTPException(404, "User not found")
        if not user.is_active:
            raise HTTPException(400, "Inactive user")
        self.user_repo.update_password(db_user=user, new_password=new_password)
        return {"message": "Password updated successfully"}
