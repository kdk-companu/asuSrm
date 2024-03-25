import os
from uuid import uuid4

from pypdf import PdfReader
from pypdf.errors import PdfReadError


class Files:

    def random_name(filename):
        """Случайное имя"""
        ext = filename.split('.')[-1]
        filename = '{}.{}'.format(uuid4().hex, ext)

        return filename

    def check_pdf(file):
        """Проверка файла на pdf"""
        try:
            PdfReader(file)
        except PdfReadError:
            return False
        else:
            return True
