from pydantic import BaseModel
from typing import List, Optional


class DiskografiItem(BaseModel):
    tahun: Optional[str] = None
    judul: Optional[str] = None
    jenis: Optional[str] = None
    format: Optional[str] = None
    pranala: List[str] = []


class ProjectResponse(BaseModel):
    nama_projek: Optional[str] = None
    date_posted: Optional[str] = None
    author: Optional[str] = None
    deskripsi: Optional[str] = None
    format: Optional[str] = None  # group/solo
    anggota: List[str] = []
    genre: Optional[str] = None
    tahun: Optional[str] = None  # year of emergence
    status: Optional[str] = None  # aktif/bubar
    diskografi: List[DiskografiItem] = []
    pranala: List[str] = []
    tags: List[str] = []
    media: List[str] = []


class ScrapeResponse(BaseModel):
    projects: List[ProjectResponse] = []