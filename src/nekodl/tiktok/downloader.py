from ..core.core import _download_generic

def download(url, *, PATH=None):
    return _download_generic(url, folder_name="Tiktok_Download", quality="best", PATH=PATH)