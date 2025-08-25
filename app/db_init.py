from sqlalchemy import create_engine, Column, String, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DB_URL = 'sqlite:///qpp.db'
engine = create_engine(DB_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

def init_db():
    class Job(Base):
        __tablename__ = 'jobs'
        job_id = Column(String, primary_key=True)
        status = Column(String)
        result = Column(JSON)
    Base.metadata.create_all(engine)
