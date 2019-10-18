from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

import jobhunter.daos.sql.common as common


class Job(common.Base):
    __tablename__ = 'jobs'
    metadata = common.METADATA

    id = Column(Integer, primary_key=True)
    company = Column(String)
    date_posted = Column(DateTime)
    description = Column(String)
    employment_type = Column(String)
    location = Column(String)
    title = Column(String)
    is_active = Column(Boolean)
    url = Column(String, primary_key=True)

    watching_user = relationship('JobWatch')


class User(common.Base):
    __tablename__ = 'users'
    metadata = common.METADATA

    id = Column(Integer, primary_key=True)
    username = Column(String(64), index=True, unique=True, primary_key=True)
    email = Column(String(120), index=True, unique=True)
    password_hash = Column(String(128))

    watched_job = relationship('JobWatch')


class JobWatch(common.Base):
    __tablename__ = 'job_watches'
    metadata = common.METADATA

    username = Column(Integer, ForeignKey('users.username'), primary_key=True)
    job_id = Column(String, ForeignKey('jobs.id'), primary_key=True) 
    


common.METADATA.create_all()
