from fastapi import FastAPI, UploadFile, Request
from fastapi.middleware.cors import CORSMiddleware

from app.utils import parse_invoice_and_send_email

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


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/invoice/gupshup/whatsapp")
async def upload_invoice(file: UploadFile, vendor_name: str, mode: str):
    import pdb; pdb.set_trace()
    await parse_invoice_and_send_email(file)
    return {"message": "email send"}


@app.post("/invoice")
async def upload_invoice(file: UploadFile):
    await parse_invoice_and_send_email(file)
    return {"message": "email send"}
