from pathlib import Path

import patoolib


class Archive:
    def check_archive(file):
        """Проверка файла на архив"""
        try:
            patoolib.test_archive(file, verbosity=-1)
        except:
            return False
        else:
            return True
