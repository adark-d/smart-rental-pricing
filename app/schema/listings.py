from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class ListingBase(BaseModel):
    title: Optional[str] = Field(None, example="Modern 2BR Apartment")
    price: Optional[int] = Field(None, gt=0, example=2500)
    region: Optional[str] = Field(None, example="Greater Accra")
    area: Optional[str] = Field(None, example="East Legon")
    bedrooms: Optional[int] = Field(None, example=2)
    bathrooms: Optional[int] = Field(None, example=1)
    house_type: Optional[str] = Field(None, example="Apartment")
    posted_date: Optional[datetime] = Field(None, example="2024-03-01T12:30:00")
    amenities: Optional[str] = Field(None, example="Air Conditioning, Balcony")
    description: Optional[str] = Field(None, example="A spacious modern apartment...")
    features: Optional[Dict[str, Any]] = Field(
        default_factory=dict, example={"furnishing": "Furnished"}
    )


class ListingShort(BaseModel):
    listing_id: str
    listing_type: Optional[str]
    title: Optional[str]
    price: Optional[int]
    region: Optional[str]
    posted_date: Optional[datetime]


class ListingCreate(ListingBase):
    listing_id: str
    listing_type: Optional[str]
    url: Optional[str]


class ListingUpdate(ListingBase):
    pass


class ListingOut(ListingCreate):
    scraped_at: Optional[datetime]

    class Config:
        orm_mode = True
