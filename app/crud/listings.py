from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.db.models.listings import Listing
from app.schema.listings import ListingCreate, ListingUpdate


def create_listing(db: Session, data: ListingCreate):
    data_dict = data.model_dump()
    db_obj = Listing(**data_dict)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_listing(db: Session, listing_id: str):
    return db.query(Listing).filter(Listing.listing_id == listing_id).first()


def get_all_listings(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    region: Optional[str] = None,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
):
    query = db.query(Listing)

    if region:
        query = query.filter(Listing.region.ilike(f"%{region}%"))
    if min_price is not None:
        query = query.filter(Listing.price >= min_price)
    if max_price is not None:
        query = query.filter(Listing.price <= max_price)

    return query.order_by(Listing.scraped_at.desc()).offset(skip).limit(limit).all()


def update_listing(db: Session, listing_id: str, data: ListingUpdate):
    db_obj = get_listing(db, listing_id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found"
        )

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(db_obj, field, value)

    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_listing(db: Session, listing_id: str):
    db_obj = get_listing(db, listing_id)
    if not db_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found"
        )

    db.delete(db_obj)
    db.commit()
