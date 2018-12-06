import os
from io import BytesIO
from zipfile import ZipFile
from flask import render_template, current_app as app


class Docx:
    @classmethod
    def _template_path(cls):
        return os.path.join(app.root_path, "..", "templates", "docx", "template.docx")

    @classmethod
    def _template(cls):
        return ZipFile(Docx._template_path(), mode="r")

    @classmethod
    def render(cls, **args):
        document = render_template("docx/document.xml", **args)
        docx = BytesIO()
        outfile = ZipFile(docx, mode="w")
        with Docx._template() as template:
            for item in template.infolist():
                if item.filename != "word/document.xml":
                    content = template.read(item.filename).decode()
                    outfile.writestr(item, content)
                else:
                    outfile.writestr(item, document)
        outfile.close()
        docx.seek(0)
        return docx.read()
