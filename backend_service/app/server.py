from typing import Union

from sqlalchemy.orm import Session

from fastapi import FastAPI, UploadFile, Request, Depends
from fastapi.middleware.cors import CORSMiddleware

from app.utils import parse_invoice_and_send_email, parse_invoice_detail_zip, send_slack_message, approve_invoice, \
    calculate_company_caas_bill_amount

from . import crud, models, schemas
from .database import SessionLocal, engine
from .schemas import ApproveInvoice

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:80",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/invoice/{invoice_id}/details")
async def upload_invoice_details(file: UploadFile, invoice_id: str):
    await parse_invoice_detail_zip(invoice_id, file)
    return {"message": "email send"}


@app.post("/invoice")
async def upload_invoice(file: UploadFile, vendor_name: str, mode: str, db: Session = Depends(get_db)):
    return await parse_invoice_and_send_email(file, vendor_name, mode, db)


@app.get("/invoice", response_model=list[schemas.Invoice])
def list_invoices(skip: int = 0, limit: int = 100, vendor_name: Union[str, None] = None, db: Session = Depends(get_db)):
    items = crud.get_items(db, skip=skip, limit=limit, vendor_name=vendor_name)
    return items


@app.get("/vendors/distinct", response_model=list[schemas.VendorDistinct])
def list_invoices(db: Session = Depends(get_db)):
    vendors = crud.get_vendors(db)
    return vendors


@app.get("/invoice-request")
def list_invoices_(vendor_name: Union[str, None] = None, month: Union[str, None] = None, is_completed: str = "false", db: Session = Depends(get_db)):
    vendors = crud.get_invoice_requests(vendor_name, month, is_completed, db)
    return vendors


@app.get("/invoice/{invoice_id}/slack")
def send_slack_message_invoices(invoice_id: str, db: Session = Depends(get_db)):
    send_slack_message(invoice_id, db)
    return {"message": "Message send"}


@app.post("/invoice/{invoice_id}/approve")
async def approve_invoice_obj(invoice_id: str, data: ApproveInvoice, db: Session = Depends(get_db)):
    return approve_invoice(invoice_id, data.approved_by, db)


@app.get("/generate-bills")
async def test_generate_bill(company_id: str, dpd_range: str, allocated_loans: int, recovered_loans: int,
                             amount_recovered: int, db: Session = Depends(get_db)):
    return calculate_company_caas_bill_amount(company_id, dpd_range, allocated_loans, recovered_loans,
                                              amount_recovered, db)
