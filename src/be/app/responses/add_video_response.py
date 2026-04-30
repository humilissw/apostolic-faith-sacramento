from pydantic import BaseModel


class AddVideoResponse(BaseModel):
    upload_name: str
    id: str
