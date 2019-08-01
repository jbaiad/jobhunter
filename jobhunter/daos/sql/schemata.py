from sqlalchemy import Column, DateTime, String

import jobhunter.daos.sql.common as common


class Job(common.Base):
    __tablename__ = 'jobs'
    metadata = common.METADATA

    company = Column(String)
    date_posted = Column(DateTime)
    description = Column(String)
    employment_type = Column(String)
    location = Column(String)
    title = Column(String)
    url = Column(String, primary_key=True)

common.METADATA.create_all()

