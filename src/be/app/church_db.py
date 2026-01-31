from datetime import date, datetime
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session

class ChurchDb:
    
    def __init__(self, conn_str: str) -> None:
        self.conn_str = conn_str
        
    def create(self) -> Engine:
        # from sqlalchemy import create_engine
        engine = create_engine(self.conn_str, echo=True)
        # engine = create_engine("sqlite://", echo=True)
        return engine

    def get_session(self) -> Session:
        eng = self.create()
        return Session(eng)
    
    def test_connect(self) -> None:
        eng = self.create()
        Base.metadata.drop_all(eng)
        Base.metadata.create_all(eng)
        with Session(eng) as session:
            test_1 = Test(
                test1=1,
                test2=2,
                test3=3,
                test4=4,
            )
            test_2 = Test(
                test1=2,
                test2=2,
                test3=3,
                test4=4,
            )
            media_item = Media(
                name = 'test',
                upload_date = datetime.now()
            )
            
            session.add_all([test_1, test_2, media_item])
            
            session.commit()
            