from pydantic import BaseModel

from app.models.mixins import IDMixin


class VersionCreateModel(BaseModel):
    version: str
    release_date: str
    data: bytes | None = None


class VersionResponseModel(IDMixin):
    version: str
    release_date: str


class VersionDataModel(VersionCreateModel, IDMixin):
    pass


class VersionDeleteModel(IDMixin):
    pass
