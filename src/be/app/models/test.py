from typing import List
from typing import Optional
from sqlalchemy import Date, ForeignKey
from sqlalchemy import String
# from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from afcapp.models.base import Base


class Test(Base):
     __tablename__ = "test"

     id: Mapped[int] = mapped_column(primary_key=True)
     test1: Mapped[int]
     test2: Mapped[int]
     test3: Mapped[int]
     test4: Mapped[int]
    
    #  test2: Mapped[int] = mapped_column(int(100))
    #  test3: Mapped[int] = mapped_column(int(100))
    #  test4: Mapped[int] = mapped_column(int(100))
     
    #  name: Mapped[str] = mapped_column(String(30))
    #  fullname: Mapped[Optional[str]]

    #  addresses: Mapped[List["Address"]] = relationship(
    #      back_populates="user", cascade="all, delete-orphan"
    #  )

     def __repr__(self) -> str:
         return f"Test(test1={self.test1!r}, test2={self.test2!r}, test3={self.test3!r}, test4={self.test4!r})"
        #  return f"User(id={self.id!r}, name={self.name!r}, fullname={self.fullname!r})"
        
class Media(Base):
    __tablename__ = "media"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    upload_date: Mapped[Date] = mapped_column(Date)