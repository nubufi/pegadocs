from pydantic import BaseModel


class ScanningRequest(BaseModel):
    data_source_id: str
