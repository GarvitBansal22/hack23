EMAIL_CONTENT = ("<html><body>Hello GupShup Team,<br><br>\n"
                 "Request you to share the detailed usage report for whatsapp with triggered and delivered count for "
                 "the {month} month of the below mentioned accounts:-\n<br><br>"
                 "<table cellspacing=\"0.5\" bgcolor=\"#000000\">"
                 "<tr bgcolor=\"#ffffff\"><th>Account</th></tr>"
                 "{table_rows}</table><br><br>\n"
                 "Thanks and Regards,<br>"
                 "Credgenics Team</body></html>")
TABLE_ROW_CONTENT = "<tr bgcolor=\"#ffffff\"><td>{account_number}</td></tr>\n"
# INVOICE_FILE_PATH = "/Users/abhinavsingh/Downloads/Invoices/"
# INVOICE_DETAILS_FILE_PATH = "/Users/abhinavsingh/Downloads/Invoices/Details"
INVOICE_FILE_PATH = "/Users/avinash.tirkey/Downloads/Invoices/"
INVOICE_DETAILS_FILE_PATH = "/Users/avinash.tirkey/Downloads/Invoices/Details/{invoice_id}"

SLACK_MESSAGE = "Please approve the {vendor_name} {mode} invoice for the allocation month of {month}"

APPROVAL_STAGES = {
    "Stage 0": {
        "next_stage": "Stage 1",
        "approver": "Approver 1"
    },
    "Stage 1": {
        "next_stage": "Stage 2",
        "approver": "Approver 2"
    }
}
