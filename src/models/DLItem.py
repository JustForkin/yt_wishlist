from models.Base import Base
from sqlalchemy import Column, Integer, DATETIME, Unicode

class DLItem(Base):
    __tablename__ = 'DLItem'

    id = Column(Integer, primary_key=True)
    utc_time = Column(DATETIME)
    url = Column(Unicode)
    path = Column(Unicode)
    status = Column(Unicode)
    progress = Column(Integer)

    def __repr__(self):
        return '<DLItem {0} at {1}>'.format(self.url, self.utc_time)

    def to_dict(self):
        return {'id': self.id,
                'utc_time': self.utc_time.strftime('%Y-%m-%d %H:%M:%S.%f') if self.utc_time else '',
                'url': self.url,
                'path': self.path,
                'status': self.status,
                'progress': self.progress}
