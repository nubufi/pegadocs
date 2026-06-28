from typing import List, Dict, Any
from app.application.services.data_source_service import DataSourceService
from app.presentation.schemas.data_source_schemas import (
    CreateDataSourceRequest,
    CreateDataSourceResponse,
    ListDataSourcesRequest,
    SASUrlRequest,
    UpdateDataSourceRequest,
    UpdateDataSourceResponse,
)


class DataSourceController:
    """Controller for data source operations"""

    def __init__(self, data_source_service: DataSourceService):
        self.data_source_service = data_source_service

    def delete_data_source(self, data_source_id: str, user_id: str) -> Dict[str, str]:
        """
        Handle delete data source request

        Args:
            data_source_id (str): The ID of the data source to delete
        Returns:
            Dict[str, str]: A message indicating the result of the deletion
        """
        self.data_source_service.delete_data_source(data_source_id, user_id)
        return {"message": f"Data source '{data_source_id}' deleted successfully"}

    def add_data_source(
        self, request: CreateDataSourceRequest, user_id: str
    ) -> CreateDataSourceResponse:
        """
        Handle add data source request

        Args:
            request (CreateDataSourceRequest): The request containing data source details
            user_id (str): The ID of the user adding the data source
        Returns:
            CreateDataSourceResponse: The response containing the created data source ID
        """
        data_source_id = self.data_source_service.add_data_source(
            user_id=user_id,
            collection_id=request.collection_id,
            data_source_name=request.name,
            data_source_type=request.type,
            config=request.config,
        )
        return CreateDataSourceResponse(data_source_id=data_source_id or "")

    def update_data_source(
        self, request: UpdateDataSourceRequest, user_id: str
    ) -> UpdateDataSourceResponse:
        """
        Handle update data source request

        Args:
            request (CreateDataSourceRequest): The request containing updated data source details
            user_id (str): The ID of the user updating the data source
        Returns:
            Dict[str, str]: A message indicating the result of the update
        """
        self.data_source_service.update_data_source(
            data_source_id=request.data_source_id,
            collection_id=request.collection_id,
            data_source_name=request.name,
            data_source_type=request.type,
            config=request.config,
            user_id=user_id,
        )
        return UpdateDataSourceResponse(
            message=f"Data source '{request.data_source_id}' updated successfully"
        )

    def list_data_sources(
        self, request: ListDataSourcesRequest
    ) -> List[Dict[str, Any]]:
        """
        Handle list data sources request

        Args:
            request (ListDataSourcesRequest): The request containing collection ID
        Returns:
            List[Dict[str, Any]]: A list of data sources associated with the collection
        """
        return self.data_source_service.list_data_sources(request.collection_id)

    def generate_sas_urls(self, request: SASUrlRequest) -> Dict[str, Dict[str, str]]:
        """Handle SAS URL generation request"""
        urls = self.data_source_service.generate_sas_urls(
            folder_name=request.folder_name, file_names=request.file_names
        )
        return {"urls": urls}
