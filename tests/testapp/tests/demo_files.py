import os

from django.core.files import File


class DemoFile:
    DIRECTORY = os.path.join(os.path.dirname(__file__), "demo_files")
    JPG = "orange.jpg"
    SVG = "smile.svg"
    XYZ = "orange.xyz"
    PDF = "test.pdf"
    EMPTY_JPG = "empty.jpg"

    def __init__(self, file_name, as_django_file=False):
        self.file_name = file_name
        self.as_django_file = as_django_file
        self.file = None

    def __enter__(self):
        file_path = os.path.join(self.DIRECTORY, self.file_name)
        self.file = open(file_path, 'rb')
        if self.as_django_file:
            self.file = File(self.file)
        return self.file

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.file:
            self.file.close()
