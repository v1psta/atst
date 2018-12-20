import os
from io import BytesIO
from zipfile import ZipFile
from flask import render_template, current_app as app


class Docx:
    DOCUMENT_FILE = "word/document.xml"

    @classmethod
    def _template_path(cls, docx_file):
        return os.path.join(app.root_path, "..", "templates", docx_file)

    @classmethod
    def _template(cls, docx_file):
        return ZipFile(Docx._template_path(docx_file), mode="r")

    @classmethod
    def _write(cls, docx_template, docx_file, document):
        with docx_template as template:
            for item in template.infolist():
                if item.filename != Docx.DOCUMENT_FILE:
                    content = template.read(item.filename).decode()
                else:
                    content = document

                docx_file.writestr(item, content)

        return docx_file

    @classmethod
    def render(
        cls,
        doc_template="docx/document.xml",
        file_template="docx/template.docx",
        **args,
    ):
        document = render_template(doc_template, **args)
        byte_str = BytesIO()
        docx_file = ZipFile(byte_str, mode="w")
        docx_template = Docx._template(file_template)
        Docx._write(docx_template, docx_file, document)
        docx_file.close()
        byte_str.seek(0)
        return byte_str
