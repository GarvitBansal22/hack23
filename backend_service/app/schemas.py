from pydantic import BaseModel


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