import sys
import re
import pdfrw
from OpenSSL import crypto

# get a signed PDF:
# wget https://blogs.adobe.com/security/SampleSignedPDFDocument.pdf

sigfile = pdfrw.PdfReader(sys.argv[1])
sigfile.read_all()
signature = next((x for x in sigfile.indirect_objects.values() if getattr(x, 'Type', None) and x.Type == '/Sig'), None)

byte_range = [int(x) for x in signature.ByteRange]
# the signature length is exactly the gap between the two document ranges
assert len(signature.Contents) == byte_range[2] - byte_range[1]

file_ = open(sys.argv[1], "rb")
pdf_bin = file_.read()
first_chunk = pdf_bin[byte_range[0]:byte_range[1]]
second_chunk = pdf_bin[byte_range[2]:(byte_range[2] + byte_range[3])]

sig_content = signature.Contents
pkcs7_data = re.sub(r'0+$', r'', sig_content[1:-2])

# this breaks; it's some kind of ASN1 data
parsed = crypto.load_pkcs7_data(crypto.FILETYPE_ASN1, pkcs7_data)

# sigfile.findindirect(36, 0)
