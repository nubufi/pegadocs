from typing import List
from app.application.services.reader_service import ReaderService
from app.infra.factories.reader import ReaderMethodFactory
from app.presentation.schemas.scanning_schemas import ScanningRequest


class ScanningController:
    """Controller for embedding operations"""

    def __init__(self, reader_service: ReaderService):
        self.reader_service = reader_service

    def scan(self, request: ScanningRequest) -> List[str]:
        """Handle website embedding request (backward compatibility)"""
        reader = ReaderMethodFactory.get_reader(request.data_source_id, 1, 1)
        docs = reader.list_resources()

        return docs
