from sqlalchemy import Column, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import relationship

from .database import Base


class AccountRecord(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(String, unique=True, index=True, nullable=False)
    followers = Column(Integer, default=0)
    following = Column(Integer, default=0)
    account_age_days = Column(Integer, default=0)
    post_count_7d = Column(Integer, default=0)
    created_at = Column(DateTime)


class PostRecord(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(String, index=True, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    text = Column(Text, nullable=False)
    source = Column(String, default="upload")


class RiskReport(Base):
    __tablename__ = "risk_reports"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(String, index=True, nullable=False)
    risk_score = Column(Float, nullable=False)
    summary = Column(Text, nullable=False)
    explanations = Column(Text)
