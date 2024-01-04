from sqlalchemy.orm import Session

from . import models, schemas


def get_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Invoices).offset(skip).limit(limit).all()


def create_user_item(db: Session, item: schemas.InvoiceCreate):
    db_item = models.Invoices(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item
