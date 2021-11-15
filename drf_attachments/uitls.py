import magic
import os


def get_mime_type(file):
    """
    Get MIME by reading the header of the file
    """
    initial_pos = file.tell()
    file.seek(0)
    mime_type = magic.from_buffer(file.read(1024), mime=True)
    file.seek(initial_pos)
    return mime_type


def get_extension(file):
    filename, file_extension = os.path.splitext(file.name)
    return file_extension.lower()


def remove(file, raise_exceptions=False):
    try:
        os.remove(file.path)
    except Exception as e:
        if raise_exceptions:
            # forward the thrown exception
            raise e
        # just continue if deletion of old file was not possible and no exceptions should be raised
