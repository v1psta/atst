import os
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
    def _write(cls, docx_template, docx_file, document_content):
        """
        This method takes an existing docx as its starting
        point and copies over every file from it to a new zip
        file, overwriting the document.xml file with new
        document content.

        zipfile.ZipFile does not provide a way to replace file
        contents in a zip in-place, so we copy over the entire
        zip archive instead.

        docx_template: The source docx file we harvest from.
        docx_file: A ZipFile instance that content from the docx_template is copied to
        document_content: The new content for the document.xml file
        """
        with docx_template as template:
            for item in template.infolist():
                if item.filename != Docx.DOCUMENT_FILE:
                    content = template.read(item.filename).decode()
                else:
                    content = document_content

                docx_file.writestr(item, content)

        return docx_file

    @classmethod
    def render(
        cls,
        file_like,
        doc_template="docx/document.xml",
        file_template="docx/template.docx",
        **args,
    ):
        document = render_template(doc_template, **args)
        with ZipFile(file_like, mode="w") as docx_file:
            docx_template = Docx._template(file_template)
            Docx._write(docx_template, docx_file, document)
        file_like.seek(0)
        return file_like
