import sys

from endesive import pdf


pdf_file = open(sys.argv[1], "rb")
cert = open(sys.argv[2], "rt")

(hashok, sigok, certok) = pdf.verify(pdf_file.read(), (cert.read(),))

pdf_file.close()
