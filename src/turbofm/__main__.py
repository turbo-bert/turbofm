import pathlib
import imaplib, ssl
import smtplib, email.mime.text
import sys
import os.path
import email
import subprocess
import mailbox
import configparser
import urllib.parse

import rich
from rich.pretty import pprint as PP
from rich.console import Console
from rich.table import Table
CONSOLE = Console()

cfg: configparser.ConfigParser
cfg = configparser.ConfigParser()
cfg.read(os.path.expanduser("~/.turbofmrc"))

import logging
import time
FORMAT = '%(asctime)s+00:00 %(levelname)10s: %(message)-80s    (%(filename)s,%(funcName)s:%(lineno)s)'
FORMAT = '%(asctime)s+00:00 %(levelname)10s: %(message)s'
logging.basicConfig(level=logging.INFO, format=FORMAT)
logging.Formatter.converter = time.gmtime


def debug_cfg(cfg, con):
    t = rich.table.Table(title="~/.turbofmrc contents", row_styles=["dim", ""])
    t.add_column("section")
    t.add_column("key")
    t.add_column("value")

    for s in cfg.sections():
        t.add_row("", "", "")
        so = cfg.options(section=s)
        # s = section title
        # so = list of keys in section

        for k in so:
            v = cfg.get(section=s, option=k)
            t.add_row("%s" % s, k, v)

    con.print(t)




#debug_cfg(cfg, CONSOLE)
cfg_ = {}

def run_init(cfg:configparser.ConfigParser, con):
    global cfg_
    cfg_['home'] = os.path.expanduser(cfg.get("main", "home"))
    logging.info("home=%s" % cfg_['home'])
    os.makedirs(cfg_['home'], exist_ok=True)
    # make dirs for each imap account:
    imap_accounts = []
    for s in cfg.sections():
        if s.startswith("imap_"):
            x = {
                'id' : s[5:]
            }
            for k in cfg.options(s):
                x[k] = cfg.get(s, k)
                if k == 'passfile':
                    x[k] = os.path.expanduser(x[k])
                    if len(x[k]) > 0:
                        x['pass'] = open(x[k]).read().replace("\r", "").split("\n")[0]

            x['home'] = os.path.join(cfg_['home'], x['id'])
            os.makedirs(x['home'], exist_ok=True)
            
            x['mbox'] = os.path.join(cfg_['home'], x['id'], 'inbox.mbox')
            if not os.path.isfile(x["mbox"]):
                pathlib.Path.touch(x["mbox"])
            
            imap_accounts.append(x)
    cfg_['imap_accounts'] = imap_accounts

def run_simple(con):
    for ia in cfg_['imap_accounts']:
        logging.info("id=%s" % ia["id"])
        box = mailbox.mbox(ia["mbox"])
        try:
            logging.info("Locking mbox")
            box.lock()
            context__ = ssl.create_default_context()

            logging.info("Connecting to server")
            conn__ = imaplib.IMAP4_SSL(host=ia['server'], port=int(ia['sslport']), ssl_context=context__)

            logging.info("Running AUTH")
            conn__.login(ia['login'], ia['pass'])

            logging.info("Selecting INBOX")
            conn__.select("INBOX", False)

            logging.info("Counting messages")
            t, d = conn__.search(None, "ALL")
            allcount = len(d[0].split())

            logging.info("Found %d message(s)" % allcount)

            for msg_number in d[0].split():
                #print(str(msg_number) + "/" + str(allcount))
                logging.info("Downloading message from server")
                msg_t, msg_d = conn__.fetch(msg_number, "(RFC822)")
                logging.info("Saving to local mbox")
                msg = email.message_from_bytes(msg_d[0][1])
                box.add(msg)
                logging.info("Marking message for deletion")
                msg_t, msg_d = conn__.store(msg_number, "+FLAGS", "\\Deleted")
            
            logging.info("Deleting messages from server")
            conn__.expunge()
            logging.info("Disconnecting from server")
            conn__.close()
            conn__.logout()

            logging.info("Releasing lock on mbox")
            box.unlock()
        except Exception as exc:
            logging.error(exc)

run_init(cfg, CONSOLE)

run_simple(CONSOLE)

sys.exit(0)
