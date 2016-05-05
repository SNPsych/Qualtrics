__author__ = 'simonyu'

import random
import uuid

import PyPDF2


def pdf_encrypt(src_pdf, dest_pdf, password):
    pdf_file = open(src_pdf, 'rb')
    pdf_reader = PyPDF2.PdfFileReader(pdf_file)
    pdf_writer = PyPDF2.PdfFileWriter()
    for page_num in range(pdf_reader.numPages):
        pdf_writer.addPage(pdf_reader.getPage(page_num))
    pdf_writer.encrypt(password)
    result_pdf = open(dest_pdf, 'wb')
    pdf_writer.write(result_pdf)
    result_pdf.close()
    pdf_file.close()


def pwd():
    alphabet = "abcdefghijklmnopqrstuvwxyz!_$"
    upperalphabet = alphabet.upper()
    pw_len = 8
    pwlist = []
    for i in range(pw_len // 3):
        pwlist.append(alphabet[random.randrange(len(alphabet))])
        pwlist.append(upperalphabet[random.randrange(len(upperalphabet))])
        pwlist.append(str(random.randrange(10)))
    for i in range(pw_len - len(pwlist)):
        pwlist.append(alphabet[random.randrange(len(alphabet))])

    random.shuffle(pwlist)
    pwd = "".join(pwlist)
    return pwd


def gen_uuid():
    return uuid.uuid4().__str__()
