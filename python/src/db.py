from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import models

engine = create_engine('sqlite:///dividends.db')
models.Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)