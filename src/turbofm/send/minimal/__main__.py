import os
import sys
import json
import smtplib
from email.mime.text import MIMEText


port = int(os.getenv("SMTP_PORT", "0"))
mail_json_filename = os.getenv("MAIL_JSON", None)

if port == 0:
    print("SMTP_PORT missing")
    sys.exit(1)


if mail_json_filename == None:
    print("MAIL_JSON missing")
    sys.exit(1)


mail_ = None
with open(mail_json_filename, 'r') as f:
    mail_ = json.loads(f.read())

msg=MIMEText(mail_["body"])
msg["from"] = mail_["from"]
msg["subject"] = mail_["subject"]
msg["to"] = mail_["to"]

server = smtplib.SMTP(host="127.0.0.1", port=port)
server.send_message(msg)
server.quit()
print("done")
