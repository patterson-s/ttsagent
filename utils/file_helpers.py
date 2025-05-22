import tempfile
import os
from typing import BinaryIO


def save_uploaded_file(uploaded_file: BinaryIO) -> str:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        return tmp_file.name


def cleanup_temp_file(file_path: str) -> None:
    if os.path.exists(file_path):
        os.unlink(file_path)


def get_file_size_kb(uploaded_file: BinaryIO) -> float:
    return round(len(uploaded_file.getvalue()) / 1024, 2)