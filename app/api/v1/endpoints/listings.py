from typing import List, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import ADMIN_KEY
from app.crud.listings import (
    create_listing,
    delete_listing,
    get_all_listings,
    get_listing,
    update_listing,
)
from app.dependencies.db import get_db
from app.schema.listings import ListingCreate, ListingOut, ListingUpdate

router = APIRouter()


@router.post(
    "/listing",
    response_model=ListingOut,
    summary="Create a single listing",
    description="Adds one new listing to the database. Background logs listing ID after insertion.",
)
def add_listing(
    listing: ListingCreate,
    db: Session = Depends(get_db),
):
    created = create_listing(db, listing)
    return created


@router.post(
    "/listings",
    response_model=List[ListingOut],
    summary="Create multiple listings",
    description="Adds multiple listings at once. Useful for batch scraping operations.",
)
def add_multiple_listings(
    listings: List[ListingCreate],
    db: Session = Depends(get_db),
):
    created_listings = [create_listing(db, listing) for listing in listings]
    return created_listings


@router.get(
    "/listings",
    response_model=List[ListingOut],
    summary="Retrieve listings",
    description="Fetches listings with optional filters by region, min price, and max price. \
    Results are sorted by most recent.",
)
def get_listings(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, le=100),
    region: Optional[str] = None,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
):
    return get_all_listings(
        db=db,
        skip=skip,
        limit=limit,
        region=region,
        min_price=min_price,
        max_price=max_price,
    )


@router.get(
    "/listing/{listing_id}",
    response_model=ListingOut,
    summary="Get listing by ID",
    description="Fetch a single listing using its unique listing_id.",
)
def get_listing_by_id(listing_id: str, db: Session = Depends(get_db)):
    db_listing = get_listing(db, listing_id)
    if not db_listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    return db_listing


@router.put(
    "/listing/{listing_id}",
    response_model=ListingOut,
    summary="Update listing",
    description="Updates an existing listing by its listing_id.",
)
def update_listing_by_id(
    listing_id: str, listing: ListingUpdate, db: Session = Depends(get_db)
):
    try:
        return update_listing(db, listing_id, listing)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete(
    "/listing/{listing_id}",
    summary="Delete listing",
    description="Deletes a single listing by its listing_id.",
)
def delete_listing_by_id(listing_id: str, db: Session = Depends(get_db)):
    try:
        delete_listing(db, listing_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"detail": "Listing deleted"}


@router.delete(
    "/listings",
    summary="Delete all listings",
    description="Truncates the listings table completely. Requires confirm=true and valid \
    admin_key header.",
)
def delete_all_listings(
    confirm: bool = Query(False),
    admin_key: str = Header(None),
    db: Session = Depends(get_db),
):
    if not confirm:
        raise HTTPException(
            status_code=400,
            detail="This will permanently delete all listings. Use ?confirm=true to proceed.",
        )

    if admin_key != ADMIN_KEY:
        raise HTTPException(status_code=403, detail="You are not authorized.")

    db.execute(text("TRUNCATE TABLE listings RESTART IDENTITY CASCADE;"))
    db.commit()
    return {"detail": "All listings have been wiped from the database."}
