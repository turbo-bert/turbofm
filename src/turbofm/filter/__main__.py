from io import StringIO
import turbofm
import turbofm.scan
import mailbox
import sys
import logging
import email.generator

logging.basicConfig(level=logging.INFO)



if len(sys.argv) == 1:
    print("""
# usage: filter SRC.mbox [ field value ]+ APPEND.mbox
#                        --------------- OR ...          
# fields: rec cc to from sub body
# values: , for OR  + for AND
""")
    sys.exit(1)


arg_infile = sys.argv[1]
logging.info("infile="+arg_infile)

arg_outfile = sys.argv[-1]
logging.info("outfile="+arg_outfile)

matcher_part = sys.argv[2:-1]

if len(matcher_part) % 2 != 0:
    #print(matcher_part)
    logging.error("Uneven number of matching argmuments - %s" % str(matcher_part))
    sys.exit(1)


try:

    stat_copied = 0
    stat_not_copied = 0

    obox = mailbox.mbox(arg_outfile)
    obox.lock()

    for msg_item in turbofm.scan.scan_mbox(arg_infile):
        copy_decision=False


        for i in range(0, int(len(matcher_part)/2)):
            k = matcher_part[i*2]
            v = matcher_part[i*2+1]
            if k == "sub":
                if str(msg_item["msg"]["subject"]).upper().find(v.upper()) >= 0:
                    copy_decision=True


        if copy_decision:
            fp = StringIO()
            g = email.generator.Generator(fp, mangle_from_=True)
            g.flatten(msg_item["msg"])
            obox.add(fp.getvalue())
            stat_copied += 1
        else:
            stat_not_copied += 1

    obox.flush()
    obox.unlock()
    obox.close()

    logging.info("copied=%d not-copied=%d" % (stat_copied, stat_not_copied))

except Exception as e:
    logging.error("Something went wrong (%s)" % str(e))
finally:
    obox.unlock()
