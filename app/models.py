from sqlalchemy import Column, String, BigInteger, Text, DateTime, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime

Base = declarative_base()

class PhotoStudio(Base):
    __tablename__ = "photo_studios"
    ps_id = Column(BigInteger, primary_key=True, autoincrement=True)
    ps_name = Column(String(100))
    road_addr = Column(String(200))
    addr = Column(String(200))
    open_hour = Column(String(4))
    closed_hour = Column(String(4))
    phone = Column(String(50))
    lat = Column(String(100))
    lng = Column(String(100))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    thumbnail_url = Column(String(255))
    kakao_id = Column(String(50), unique=True)
    homepage_url = Column(String(255))
    sido = Column(String(150))
    gungu = Column(String(100))
    dongmyeon = Column(String(100))

    reviews = relationship("Review", back_populates="studio")


class Review(Base):
    __tablename__ = "review"
    review_id = Column(BigInteger, primary_key=True, autoincrement=True)
    rating = Column(Float)
    content = Column(Text)
    image_url = Column(String(255))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    user_id = Column(BigInteger, ForeignKey("user.user_id"))
    ps_id = Column(BigInteger, ForeignKey("photo_studios.ps_id"))

    studio = relationship("PhotoStudio", back_populates="reviews")


class User(Base):
    __tablename__ = "user"
    user_id = Column(BigInteger, primary_key=True, autoincrement=True)
    email = Column(String(100), unique=True)
    nick_name = Column(String(100))
    password = Column(String(255))
    telno = Column(String(50))
    sns_id = Column(String(255))
    sns_type = Column(String(255))
    sns_email = Column(String(100), unique=True)
    connected_sns = Column(String(10))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
