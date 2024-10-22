from io import StringIO
import turbofm
import turbofm.scan
import mailbox
import sys
import logging
import email.generator
import re



def html_readable(src):
    res = src.replace("<br>", " ").replace("<BR>", " ").replace("<br/>", " ").replace("<BR/>", " ")

    small_droplets = [ '<html>', '</html>', '<body>', '</body>', '&nbsp;', '<head>', '</head>', '</div>', '&quot;', '<ul>', '</ul>' ]
    for s in small_droplets:
        res = res.replace(s, ' ')
        res = res.replace(s.upper(), ' ')

    res = res.replace('<li>', '[')
    res = res.replace('</li>', ']')

    kill_meta = re.compile(r"<meta[^>]*>")
    res = re.sub(kill_meta, '', res)

    kill_div = re.compile(r"<div[^>]*>")
    res = re.sub(kill_div, ' ', res)

    reduce_space = re.compile(r" +")
    res = re.sub(reduce_space, ' ', res)

    return res.strip()




logging.basicConfig(level=logging.INFO)



if len(sys.argv) == 1:
    print("""
# usage: bodies SRC.mbox OUTFILE
""")
    sys.exit(1)


arg_infile = sys.argv[1]
logging.info("infile="+arg_infile)

arg_outfile = sys.argv[2]
logging.info("outfile="+arg_outfile)


try:

    with open(arg_outfile, 'w') as outfile:

        for msg_item in turbofm.scan.scan_mbox(arg_infile):
            msg = msg_item["msg"]
            if msg.is_multipart():
                body_plain=""
                body_html=""
                for part in msg.walk():
                    if part.get_content_type()=="text/plain" and "attachment" not in str(part.get("Content-Disposition")):
                        body_plain = part.get_payload(decode=True).decode(errors='ignore')
                    if part.get_content_type()=="text/html" and "attachment" not in str(part.get("Content-Disposition")):
                        body_html = part.get_payload(decode=True).decode(errors='ignore')
                if body_plain == "":
                    body_html = body_html.replace("\r", "").replace("\n", "").strip()
                    body_html = html_readable(body_html)
                    outfile.write(body_html)
                else:
                    body_plain = body_plain.replace("\r", "").replace("\n", "").strip()
                    body_plain = html_readable(body_plain)
                    outfile.write(body_plain)
            else:
                body = msg.get_payload(decode=True).decode(errors='ignore')
                body = body.replace("\r", "").replace("\n", "").strip()
                body = html_readable(body)
                outfile.write(body)
            outfile.write("\n")

except Exception as e:
    logging.error("Something went wrong (%s)" % str(e))
