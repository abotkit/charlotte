from abc import ABC, abstractmethod


class IObjectStorageHandler(ABC):

    @abstractmethod
    def make_bucket(self, bucket_name: str, location: str):
        raise NotImplementedError

    @abstractmethod
    def upload_file(self, bucket_name: str, object_name: str, file_path: str):
        raise NotImplementedError

    @abstractmethod
    def download_file(self, bucket_name: str, object_name: str, file_path: str):
        raise NotImplementedError

    @abstractmethod
    def delete_file(self, bucket_name: str, object_name: str):
        raise NotImplementedError

    @abstractmethod
    def delete_files(self, bucket_name: str, files: list):
        raise NotImplementedError

    @abstractmethod
    def remove_bucket(self, bucket_name: str):
        raise NotImplementedError

    @abstractmethod
    def list_objects(self, bucket_name: str, recursive: bool):
        raise NotImplementedError

    @abstractmethod
    def bucket_exists(self, bucket_name: str):
        raise NotImplementedError