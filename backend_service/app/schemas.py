from pydantic import BaseModel
import uuid


class InvoiceBase(BaseModel):
    vendor_name: str
    mode: str
    file_name: str
    allocation_month: str


class InvoiceCreate(InvoiceBase):
    pass


class Invoice(InvoiceBase):
    id: int

    class Config:
        orm_mode = True


class VendorDistinct(BaseModel):
    vendor_name: str


class MonthlyCounts(BaseModel):
    company_id: uuid.UUID
    vendor: str
    month_year_string: str
    message_count_monthly: int


class InvoicesCountsBase(BaseModel):
    invoice_id: int
    approver_stage: str
    count_db: int
    count_vendor: int


class InvoicesCountsCreate(InvoicesCountsBase):
    pass


# Request models
class ApproveInvoice(BaseModel):
    approved_by: str
