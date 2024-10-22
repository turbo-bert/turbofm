import turbofm
import turbofm.scan
import sys


for item in turbofm.scan.scan_mbox(sys.argv[1]):
    print(item["id"])
    print(item["msg"]["subject"])
