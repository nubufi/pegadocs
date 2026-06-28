from typing import Dict, Literal, List
from pydantic import BaseModel


class SASUrlRequest(BaseModel):
    folder_name: str
    file_names: List[str]


class SasUrlItem(BaseModel):
    content_type: str
    url: str


class SASUrlResponse(BaseModel):
    urls: Dict[str, Dict[str, SasUrlItem]]


class CreateDataSourceRequest(BaseModel):
    collection_id: str
    name: str
    type: Literal[
        "onedrive",
        "sharepoint",
        "google_drive",
        "file",
        "website",
        "github",
        "gitlab",
        "s3",
        "dropbox",
        "azure_blob",
        "jira",
    ]

    config: dict


class CreateDataSourceResponse(BaseModel):
    data_source_id: str


class UpdateDataSourceRequest(BaseModel):
    data_source_id: str
    collection_id: str
    name: str
    type: Literal[
        "onedrive",
        "sharepoint",
        "google_drive",
        "file",
        "website",
        "github",
        "gitlab",
        "s3",
        "dropbox",
        "azure_blob",
        "jira",
    ]

    config: dict


class UpdateDataSourceResponse(BaseModel):
    message: str


class ListDataSourcesRequest(BaseModel):
    collection_id: str


class ListDataSources(BaseModel):
    id: str
    collection_id: str
    type: Literal[
        "onedrive",
        "sharepoint",
        "google_drive",
        "file",
        "website",
        "github",
        "gitlab",
        "s3",
        "dropbox",
        "azure_blob",
        "jira",
    ]
    name: str
    created_at: str
    config: dict
    size_in_gb: float
