from sqlalchemy.ext.declarative import declarative_base

# base class instance shared among all declaratives
# so their relationship is mapped correctly
Base = declarative_base()