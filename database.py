from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLITE3 database url
SQLALCHEMY_DATABASE_URL = "sqlite:///./todosapp.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

# Postgresql database url
# used %40 to escape @ in the password as @ is a special character in the url and needs to be encoded.
# SQLALCHEMY_DATABASE_URL = "postgresql://postgres:Hyderabad%4012345@localhost/TodoApplicationDatabase"
# # removing connect_args for postgresql as it's not needed.[it's only ]
# engine = create_engine(SQLALCHEMY_DATABASE_URL)

session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)  
  
appBase = declarative_base() 