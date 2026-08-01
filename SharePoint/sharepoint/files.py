"""
File upload/download helpers.
"""

from pathlib import Path


def upload_file(ctx, folder_server_relative_url, local_file_path):
    """Uploads a local file (up to 4MB) into the given server-relative folder,
    e.g. "/sites/mysite/Shared Documents". Returns the created File object."""
    local_path = Path(local_file_path)
    content = local_path.read_bytes()

    target_folder = ctx.web.get_folder_by_server_relative_url(folder_server_relative_url)
    uploaded_file = target_folder.upload_file(local_path.name, content)
    ctx.execute_query()
    return uploaded_file


def download_file(ctx, file_server_relative_url, local_file_path):
    """Downloads a file from the given server-relative URL,
    e.g. "/sites/mysite/Shared Documents/report.docx", to a local path."""
    target_file = ctx.web.get_file_by_server_relative_url(file_server_relative_url)
    with open(local_file_path, "wb") as f:
        target_file.download(f).execute_query()
