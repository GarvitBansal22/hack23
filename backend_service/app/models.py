from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship

from app.database import Base


class Invoices(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    vendor_name = Column(String)
    mode = Column(String)
    file_name = Column(String)


class InvoicesCounts(Base):
    __tablename__ = "invoice_counts"

    id = Column(Integer, primary_key=True, index=True)
    approver_stage = Column(String)
    last_notification_send = Column(DateTime)
    count_db = Column(Integer)
    counts_vendor = Column(Integer)
    created = Column(DateTime)
