from fastapi import FastAPI, UploadFile

from backend_service.app.utils import parse_invoice_and_send_email

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/uploadInvoice/")
async def upload_invoice(file: UploadFile):
    await parse_invoice_and_send_email(file.file)
    return {"message": "email send"}
