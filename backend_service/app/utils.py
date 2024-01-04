import aiofiles
import datetime
import PyPDF2
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import aiosmtplib

from app.settings import SMTP_PORT, SMTP_SERVER
from app.constants import EMAIL_CONTENT, TABLE_ROW_CONTENT, INVOICE_FILE_PATH
from app.crud import create_user_item
from . import schemas


async def parse_invoice_and_send_email(file, vendor_name, mode, db):
    file_name = await save_invoice_to_disk(file)
    item = {
        "file_name": file_name,
        "vendor_name": vendor_name,
        "mode": mode
    }
    item = schemas.InvoiceCreate(**item)
    create_user_item(db=db, item=item)
    account_numbers, month = get_account_numbers_from_invoice(file.file)
    await send_email("Gupshup account numbers 11", prepare_email_content(account_numbers, month))


async def save_invoice_to_disk(file):
    file_name = file.filename + datetime.date.today().strftime("%Y-%m-%d") 
    file_path = INVOICE_FILE_PATH + file_name
    async with aiofiles.open(file_path, mode='wb') as f:
        await f.write(file.file.read())
    return file_name


def prepare_email_content(account_numbers, allocation_month):
    table_rows = "".join([TABLE_ROW_CONTENT.format(account_number=account_number) for account_number in account_numbers])
    return EMAIL_CONTENT.format(month=allocation_month, table_rows=table_rows)


def get_account_numbers_from_invoice(pdf_file_obj):
    pdf_reader = PyPDF2.PdfReader(pdf_file_obj)

    number_of_pages = len(pdf_reader.pages)

    account_numbers = list()
    month = ""

    for i in range(number_of_pages-1):
        page_obj = pdf_reader.pages[i]
        page_text = page_obj.extract_text()
        page_text = page_text.split("\n")

        index_account_key = -1
        for index_text, text in enumerate(page_text):
            text = text.strip().lower()
            if re.search("^billing period.*$", text):
                month = text.split(":")[1].strip().split()[1]
            if re.search("^account.*$", text):
                index_account_key = index_text
                break
        # print(f"Index for account keyword is {index_account_key} for page number {i}")

        page_text = page_text[index_account_key:]

        flag = 0
        for text in page_text:
            text = text.strip().lower()
            if flag == 1:
                break
            if not text[0].isalpha():
                account_numbers.append(text.strip().split()[0])
            elif 'taxable amount' in text:
                flag = 1

        # print(pageText)
    account_numbers = list(set(account_numbers))
    return account_numbers, month


async def send_email(subject, content):
    message = MIMEMultipart("alternative")
    message["From"] = "sender@example.com"
    message["To"] = "receiver@example.com"
    message["Subject"] = subject
    part1 = MIMEText(content, "html")
    message.attach(part1)

    await aiosmtplib.send(message, hostname=SMTP_SERVER, port=SMTP_PORT)
