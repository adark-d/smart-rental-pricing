from sqlalchemy import TIMESTAMP, Column, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB

from app.db.base import Base


class Listing(Base):
    __tablename__ = "listings"

    id = Column(Integer, primary_key=True, index=True)
    listing_id = Column(String, unique=True, nullable=False, index=True)
    url = Column(Text)
    title = Column(Text)
    price = Column(Integer)
    region = Column(String)
    area = Column(String)
    bedrooms = Column(Integer)
    bathrooms = Column(Integer)
    house_type = Column(String)
    posted_date = Column(TIMESTAMP, index=True)
    amenities = Column(Text)
    description = Column(Text)
    features = Column(JSONB)
    scraped_at = Column(TIMESTAMP, server_default=func.now())
