from sqlalchemy.orm import Session

from . import models, schemas


def get_items(db: Session, skip: int = 0, limit: int = 100, vendor_name=None):
    if vendor_name is not None:
        return db.query(models.Invoices).filter(models.Invoices.vendor_name == vendor_name).offset(skip).limit(limit)
    return db.query(models.Invoices).offset(skip).limit(limit).all()


def get_invoice(db: Session, invoice_id):
    return db.query(models.Invoices).filter(models.Invoices.id == invoice_id).first()


def create_user_item(db: Session, item: schemas.InvoiceCreate):
    db_item = models.Invoices(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def get_vendors(db: Session):
    return db.query(models.Invoices.vendor_name).distinct().all()


def get_vendor_total_count(vendor_name, month_year_string: str, mode, db: Session):
    return db.query(models.MonthlyCounts).filter(models.MonthlyCounts.vendor == vendor_name,  models.MonthlyCounts.month_year_string == month_year_string, models.MonthlyCounts.mode == mode).first()


def get_invoice_requests(vendor_name, month_year_string, is_completed, db: Session):
    if is_completed.lower() in ["false", "0"]:
        stages = ("Stage 0", "Stage 1", "Stage 2", "Stage 3", "Stage 4")
    else:
        stages = ("Stage 5",)

    if vendor_name and month_year_string:
        return db.query(models.InvoicesCounts).join(models.Invoices, models.Invoices.id == models.InvoicesCounts.invoice_id).filter(models.Invoices.vendor_name == vendor_name, models.Invoices.allocation_month == month_year_string, models.InvoicesCounts.approver_stage.in_(stages)).all()
    if vendor_name:
        return db.query(models.InvoicesCounts).join(models.Invoices, models.Invoices.id == models.InvoicesCounts.invoice_id).filter(models.Invoices.vendor_name == vendor_name, models.InvoicesCounts.approver_stage.in_(stages)).all()
    if month_year_string:
        return db.query(models.InvoicesCounts).join(models.Invoices, models.Invoices.id == models.InvoicesCounts.invoice_id).filter(models.Invoices.allocation_month == month_year_string, models.InvoicesCounts.approver_stage.in_(stages)).all()

    return db.query(models.InvoicesCounts).join(models.Invoices,models.Invoices.id == models.InvoicesCounts.invoice_id).filter(models.InvoicesCounts.approver_stage.in_(stages)).all()


def create_invoice_counts(db: Session, item: schemas.InvoicesCountsCreate):
    db_item = models.InvoicesCounts(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def update_invoice_counts(db: Session, invoice_count: models.InvoicesCounts):
    db.add(invoice_count)
    db.commit()
    db.refresh(invoice_count)
    return invoice_count
