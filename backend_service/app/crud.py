from sqlalchemy.orm import Session

from . import models, schemas


def get_items(db: Session, skip: int = 0, limit: int = 100, vendor_name=None):
    if vendor_name is not None:
        return db.query(models.Invoices).filter(models.Invoices.vendor_name == vendor_name).offset(skip).limit(limit)
    return db.query(models.Invoices).offset(skip).limit(limit).all()


def create_user_item(db: Session, item: schemas.InvoiceCreate):
    db_item = models.Invoices(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def get_vendors(db: Session):
    return db.query(models.Invoices.vendor_name).distinct().all()


def get_vendor_total_count(vendor_name, month_year_string: str, db: Session):
    return db.query(models.MonthlyCounts).filter(models.MonthlyCounts.vendor == vendor_name,  models.MonthlyCounts.month_year_string == "2023-02")


def create_invoice_counts(db: Session, item: schemas.InvoicesCountsCreate):
    db_item = models.InvoicesCounts(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item