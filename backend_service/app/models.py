from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship

from app.database import Base


class Invoices(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    vendor_name = Column(String)
    mode = Column(String)
    file_name = Column(String)
    allocation_month = Column(String)

    invoice_count = relationship("InvoicesCounts", back_populates="invoice")


class InvoicesCounts(Base):
    __tablename__ = "invoice_counts"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"))
    approver_stage = Column(String)
    last_notification_send = Column(DateTime)
    count_db = Column(Integer)
    count_vendor = Column(Integer)
    created = Column(DateTime)

    invoice = relationship("Invoices", back_populates="invoice_count")


class MonthlyCounts(Base):
    __tablename__ = "monthly_counts"

    company_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vendor = Column(String, primary_key = True)
    month_year_string = Column(String, primary_key = True)
    message_count_monthly = Column(Integer)
    mode = Column(String)
