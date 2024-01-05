import io

import aiofiles
import datetime
import PyPDF2
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import aiosmtplib
import zipfile
from slack_sdk import WebClient
from sqlalchemy.orm import Session

from app.settings import SMTP_PORT, SMTP_SERVER, SLACK_TOKEN, SLACK_CHANNEL
from app.constants import EMAIL_CONTENT, TABLE_ROW_CONTENT, INVOICE_FILE_PATH, INVOICE_DETAILS_FILE_PATH, SLACK_MESSAGE, \
    APPROVAL_STAGES
from app.crud import create_user_item, get_vendor_total_count, create_invoice_counts, get_invoice, update_invoice_counts
from . import schemas


async def parse_invoice_and_send_email(file, vendor_name, mode, db):
    file_name = await save_invoice_to_disk(file)
    counts = 0
    if vendor_name == "gupshup" and mode == "whatsapp":
        account_numbers, month = get_account_numbers_and_month_from_invoice(file.file)
        await send_email(f"Gupshup account numbers: {month}", prepare_email_content(account_numbers, month))
    else:
        # call method to save to db
        counts, month = calculate_invoice_counts_and_month(file.file)
        notify_pending_approval_in_slack(
            vendor_name, mode, datetime.datetime.strptime(month.capitalize(), "%b-%y").strftime("%Y-%m")
        )

    month = datetime.datetime.strptime(month.capitalize(), "%b-%y").strftime("%Y-%m")
    item = {
        "file_name": file_name,
        "vendor_name": vendor_name,
        "mode": mode,
        "allocation_month": month

    }
    item = schemas.InvoiceCreate(**item)
    invoice = create_user_item(db=db, item=item)

    if not(vendor_name == "gupshup" and mode == "whatsapp"):
        store_counts_in_db(invoice.id, vendor_name, month, counts, mode, db)

    return invoice


async def parse_invoice_detail_zip(invoice_id, file):
    with zipfile.ZipFile(io.BytesIO(file.file.read()), "r") as zf:
        file_names = zf.namelist()
        base_path = INVOICE_DETAILS_FILE_PATH.format(invoice_id=invoice_id)
        zf.extractall(path=base_path)
        counts = calculate_excel_counts(base_path, file_names)


async def save_invoice_to_disk(file):
    file_name = file.filename.split(".")[0]
    file_extension = file.filename.split(".")[-1]
    file_name = file_name + "_" + datetime.date.today().strftime("%Y-%m-%d") + "." + file_extension
    file_path = INVOICE_FILE_PATH + file_name
    async with aiofiles.open(file_path, mode='wb') as f:
        await f.write(file.file.read())
    return file_name


def prepare_email_content(account_numbers, allocation_month):
    table_rows = "".join([TABLE_ROW_CONTENT.format(account_number=account_number) for account_number in account_numbers])
    return EMAIL_CONTENT.format(month=allocation_month, table_rows=table_rows)


def get_account_numbers_and_month_from_invoice(pdf_file_obj):
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


def calculate_excel_counts(base_path: str, file_names: list):
    count_of_communication = 0
    for file_name in file_names:
        complete_file_path = str(Path(base_path) / Path(file_name))
        df = pd.read_csv(complete_file_path)
        # acoount_number = file_name.split("_")[0]
        # summation_dict[acoount_number] = df['NUMBER MESSAGES'].sum()
        count_of_communication += df['NUMBER MESSAGES'].sum()
        del df
    return count_of_communication


def calculate_invoice_counts_and_month(invoice_pdf_file):
    pdf_reader = PyPDF2.PdfReader(invoice_pdf_file)

    number_of_pages = len(pdf_reader.pages)
    count_of_transactions = "0"
    month = ""

    for i in range(number_of_pages - 1):
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

        page_text = page_text[index_account_key:]
        flag = 0
        for text in page_text:
            text = text.strip().lower()
            if flag == 1:
                break
            if not text[0].isalpha():
                count_of_transactions = text.strip().split()[3]
                flag = 1
            elif 'taxable amount' in text:
                flag = 1

    count_of_transactions = int(count_of_transactions.replace(",", ""))
    return count_of_transactions, month


def store_counts_in_db(invoice_id, vendor_name, month_year_string, count_invoice, mode, db):
    count_db = get_vendor_total_count(vendor_name, month_year_string, mode, db)
    if not count_db:
        count_db = 0
    else:
        count_db = count_db.message_count_monthly
    item = {
        "approver_stage": "Initial Stage",
        "vendor_name": vendor_name,
        "count_db": count_db,
        "count_vendor": count_invoice,
        "invoice_id": invoice_id
    }

    item = schemas.InvoicesCountsCreate(**item)
    invoice_count = create_invoice_counts(db=db, item=item)


def send_slack_message(invoice_id: str, db: Session):
    invoice = get_invoice(db, invoice_id)
    notify_pending_approval_in_slack(invoice.vendor_name, invoice.mode, invoice.allocation_month)
    invoice_count = invoice.invoice_count[0]
    invoice_count.last_notification_send = datetime.now()
    return update_invoice_counts(db, invoice_count)


def notify_pending_approval_in_slack(vendor_name, mode, month):
    message = SLACK_MESSAGE.format(
        vendor_name=vendor_name, mode=mode,
        month=datetime.datetime.strptime(month, "%Y-%m").strftime("%b, %y"))
    send_notification_slack(message)


def send_notification_slack(message_text):
    client = WebClient(token=SLACK_TOKEN)
    response = client.chat_postMessage(channel=SLACK_CHANNEL, text=message_text)


def approve_invoice(invoice_id, approved_by, db):
    invoice = get_invoice(db, invoice_id)
    invoice_count = invoice.invoice_count[0]
    current_approval_state = invoice_count.approver_stage

    if not approved_by == APPROVAL_STAGES[current_approval_state]["approver"]:
        return False

    invoice_count.approver_stage = APPROVAL_STAGES[current_approval_state]["next_stage"]
    return update_invoice_counts(db, invoice_count)
