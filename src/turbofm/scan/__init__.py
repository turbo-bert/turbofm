import mailbox

def scan_mbox(filename):
    box = mailbox.mbox(filename, create=False)
    for msg in box:
        id = msg["message-id"]
        id = id.replace("\r", " ")
        id = id.replace("\n", " ")
        id = id.strip()
        yield dict({"id": id, "msg": msg})
    box.close()