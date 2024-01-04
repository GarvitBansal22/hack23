from pydantic import BaseModel


class InvoiceBase(BaseModel):
    vendor_name: str
    mode: str
    file_name: str


class InvoiceCreate(InvoiceBase):
    pass


class Invoice(InvoiceBase):
    id: int

    class Config:
        orm_mode = True