from zoneinfo import ZoneInfo

from sqlalchemy import Column, String, BigInteger, Text, DateTime, Float, ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime

Base = declarative_base()

def kst_now():
    return datetime.datetime.now(ZoneInfo("Asia/Seoul"))

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
    created_at = Column(DateTime, default=kst_now)
    updated_at = Column(DateTime, default=kst_now, onupdate=kst_now)
    thumbnail_url = Column(Text)
    kakao_id = Column(String(50), unique=True)
    homepage_url = Column(String(255))
    sido = Column(String(150))
    gungu = Column(String(100))
    dongmyeon = Column(String(100))

    reviews = relationship("Review", back_populates="studio")

    categories = relationship("PhotoStudioCategory", back_populates="studio")

    images = relationship("PhotoStudioImage", back_populates="studio", cascade="all, delete-orphan")

    favorites = relationship("FavoriteStudio", back_populates="studio", cascade="all, delete-orphan")

class Review(Base):
    __tablename__ = "review"
    review_id = Column(BigInteger, primary_key=True, autoincrement=True)
    rating = Column(Float)
    content = Column(Text)
    image_url = Column(String(255))
    created_at = Column(DateTime, default=kst_now)
    updated_at = Column(DateTime, default=kst_now, onupdate=kst_now)
    user_id = Column(BigInteger, ForeignKey("user.user_id"))
    ps_id = Column(BigInteger, ForeignKey("photo_studios.ps_id"))

    studio = relationship("PhotoStudio", back_populates="reviews")
    writer = relationship("User", back_populates="reviews")

class User(Base):
    __tablename__ = "user"
    user_id = Column(BigInteger, primary_key=True, autoincrement=True)
    email = Column(String(100), unique=True)
    nick_name = Column(String(100))
    profile_image = Column(Text)
    password = Column(String(255))
    telno = Column(String(50))
    sns_id = Column(String(255))
    sns_type = Column(String(255))
    sns_email = Column(String(100), unique=True)
    connected_sns = Column(String(10))
    created_at = Column(DateTime, default=kst_now)
    updated_at = Column(DateTime, default=kst_now, onupdate=kst_now)
    recent_password_verified_at = Column(DateTime(timezone=True), default=kst_now)
    role = Column(String(100), default="user") # admin or user

    reviews = relationship("Review", back_populates="writer")
    favorites = relationship("FavoriteStudio", back_populates="user", cascade="all, delete-orphan")

class Category(Base):
    __tablename__ = "category"

    category_id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=kst_now)
    updated_at = Column(DateTime, default=kst_now)

    studio = relationship("PhotoStudioCategory", back_populates="category")

class PhotoStudioCategory(Base):
    __tablename__ = "photo_studio_category"

    psc_id = Column(BigInteger, primary_key=True, autoincrement=True)
    category_id = Column(BigInteger, ForeignKey("category.category_id"), nullable=False)
    ps_id = Column(BigInteger, ForeignKey("photo_studios.ps_id"), nullable=False)
    created_at = Column(DateTime, default=kst_now)
    updated_at = Column(DateTime, default=kst_now, onupdate=kst_now)

    category = relationship("Category", back_populates="studio")
    studio = relationship("PhotoStudio", back_populates="categories")


class PhotoStudioImage(Base):
    __tablename__ = "photo_studio_images"

    psi_id       = Column(BigInteger, primary_key=True, autoincrement=True)
    ps_id        = Column(BigInteger, ForeignKey("photo_studios.ps_id"), nullable=False, index=True)
    ps_image     = Column(Text)
    description  = Column(Text, nullable=True)
    created_at   = Column(DateTime, default=kst_now)
    updated_at   = Column(DateTime, default=kst_now, onupdate=kst_now)

    studio = relationship("PhotoStudio", back_populates="images")

class FavoriteStudio(Base):
    __tablename__ = "favorite_studio"
    fs_id      = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id    = Column(BigInteger, ForeignKey("user.user_id"), nullable=False)
    ps_id      = Column(BigInteger, ForeignKey("photo_studios.ps_id"), nullable=False)
    created_at = Column(DateTime, default=kst_now)

    # 중복 찜 방지
    __table_args__ = (
        UniqueConstraint("user_id", "ps_id", name="uq_favorite_user_studio"),
    )

    user = relationship("User", back_populates="favorites")
    studio = relationship("PhotoStudio", back_populates="favorites")