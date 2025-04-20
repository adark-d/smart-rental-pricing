import datetime
import os

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.dependencies.db import get_db
from app.dependencies.security import require_admin

router = APIRouter()


@router.get("/version", summary="Get API version info")
def version_info():
    return {
        "version": "1.0.0",
        "last_updated": datetime.datetime.utcnow().isoformat(),
        "build": os.getenv("BUILD_SHA", "dev"),
    }


@router.get(
    "/count",
    summary="Count total listings",
    description="Returns total listings, as well as breakdown by rent and sale.",
    dependencies=[Depends(require_admin)],
)
def count_listings(db: Session = Depends(get_db)):
    total = db.execute(text("SELECT COUNT(*) FROM listings")).scalar()
    rent = db.execute(
        text("SELECT COUNT(*) FROM listings WHERE listing_type = 'rent'")
    ).scalar()
    sale = db.execute(
        text("SELECT COUNT(*) FROM listings WHERE listing_type = 'sale'")
    ).scalar()

    return {
        "total_listings": total,
        "rent_listings": rent,
        "sale_listings": sale,
    }


@router.get(
    "/export",
    summary="Export all listings as JSON",
    dependencies=[Depends(require_admin)],
)
def export_listings(db: Session = Depends(get_db)):
    result = db.execute(text("SELECT * FROM listings;"))
    keys = result.keys()
    return [dict(zip(keys, row)) for row in result.fetchall()]
