from sqlalchemy import Column, Integer, String
from database import Base

class Timetable(Base):
    __tablename__ = "timetable"

    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String)
    teacher = Column(String)
    room = Column(String)
    class_name = Column(String)
    day = Column(String)
    slot = Column(String)
