from sqlalchemy.orm import Session

from fastapi import FastAPI, UploadFile, Request, Depends
from fastapi.middleware.cors import CORSMiddleware

from app.utils import parse_invoice_and_send_email

from . import crud, models, schemas
from .database import SessionLocal, engine

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


@app.post("/invoice/gupshup/whatsapp")
async def upload_invoice(file: UploadFile, vendor_name: str, mode: str, db: Session = Depends(get_db)):
    await parse_invoice_and_send_email(file, vendor_name, mode, db)
    return {"message": "email send"}


@app.post("/invoice")
async def upload_invoice(file: UploadFile):
    # await parse_invoice_and_send_email(file)
    return {"message": "email send"}

@app.get("/get-invoices", response_model=list[schemas.Invoice])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_items(db, skip=skip, limit=limit)
    return items
