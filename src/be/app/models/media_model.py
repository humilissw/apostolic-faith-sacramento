from sqlalchemy import Date
from sqlalchemy import String
# from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from afcapp.models.base import Base
# https://docs.sqlalchemy.org/en/20/orm/quickstart.html#declare-models        
class Media(Base):
    __tablename__ = "media"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    upload_date: Mapped[Date] = mapped_column(Date)