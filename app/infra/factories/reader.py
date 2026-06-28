from app.application.protocols.reader_protocol import ReaderProtocol
from app.infra.config import settings
from app.infra.utils.encrypt_utils import decrypt_dict
from app.infra.utils.supabase_utils import fetch_items
from app.infra.adapters.readers.web import WebReader
from app.infra.adapters.readers.file import FileReader
from app.infra.adapters.readers.s3 import AWSS3Reader
from app.infra.adapters.readers.github import GithubReader
from app.infra.adapters.readers.gitlab import GitlabReader
from app.infra.adapters.readers.dropbox import DropboxReader
from app.infra.adapters.readers.google_drive import GoogleDriveReader
from app.infra.adapters.readers.onedrive import OneDriveReader
from app.infra.adapters.readers.sharepoint import SharePointReader
from app.infra.adapters.readers.azure_blob import AzureStorageBlobReader
from app.infra.adapters.readers.jira import JiraReader

reader_map = {
    "website": WebReader,
    "file": FileReader,
    "s3": AWSS3Reader,
    "github": GithubReader,
    "gitlab": GitlabReader,
    "dropbox": DropboxReader,
    "google_drive": GoogleDriveReader,
    "onedrive": OneDriveReader,
    "sharepoint": SharePointReader,
    "azure_blob": AzureStorageBlobReader,
    "jira": JiraReader,
}


class ReaderMethodFactory:
    """Factory for creating embedding methods"""

    @staticmethod
    def get_reader(
        data_source_id: str, chunk_size: int, chunk_overlap: int
    ) -> ReaderProtocol:
        """
        Get the appropriate embedding method based on the collection_id.

        Args:
            data_source_id (str): The ID of the data source.

        Returns:
            ReaderProtocol: An instance of the appropriate embedding method.
        """
        resp = fetch_items(settings.DATA_SOURCES_TABLE_NAME, "id", data_source_id)
        if not resp:
            raise ValueError(f"Data source with ID {data_source_id} does not exist.")

        config = decrypt_dict(resp[0]["config"])
        data_source_type = resp[0]["type"]

        reader_class = reader_map[data_source_type]

        return reader_class(data_source_id, config, chunk_size, chunk_overlap)
