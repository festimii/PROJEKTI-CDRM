import os

def clean_and_check_utf8(file_path):
    with open(file_path, 'rb') as f:
        content = f.read()

    # Remove BOM if present
    if content.startswith(b'\xef\xbb\xbf'):
        content = content[3:]

    # Remove null bytes
    content = content.replace(b'\x00', b'')

    with open(file_path, 'wb') as f:
        f.write(content)

clean_and_check_utf8('C:\\Users\\festimbeqiri\\Desktop\\PROJEKTI-CDRM\\cubaapp\\models.py')
