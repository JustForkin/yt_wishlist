from models.Base import Base
from sqlalchemy import Column, Integer, DATETIME, Unicode, String

class DLItem(Base):
    __tablename__ = 'DLItem'

    id = Column(Integer, primary_key=True)
    utc_time = Column(DATETIME, index=True)
    title = Column(Unicode)
    url = Column(String(80), index=True)
    thumb_url = Column(String(80))
    duration = Column(Integer)
    path = Column(Unicode)
    status = Column(Unicode)
    progress = Column(Integer)

    def __repr__(self):
        return '<DLItem {0} at {1}>'.format(self.url, self.utc_time)

    def to_dict(self):
        return {'id': self.id,
                'utc_time': self.utc_time.strftime('%Y-%m-%d %H:%M:%S.%f') if self.utc_time else '',
                'title': self.title,
                'url': self.url,
                'thumb_url': self.thumb_url,
                'duration': self.duration,
                'path': self.path,
                'status': self.status,
                'progress': self.progress}
