from persistence.object_storage.iobjectstorage_handler import IObjectStorageHandler


class PlaceholderStorageHandler(IObjectStorageHandler):

    def make_bucket(self, bucket_name: str, location: str):
        pass

    def upload_file(self, bucket_name: str, object_name: str, file_path: str):
        pass

    def download_file(self, bucket_name: str, object_name: str, file_path: str):
        pass

    def delete_file(self, bucket_name: str, object_name: str):
        pass

    def delete_files(self, bucket_name: str, files: list):
        pass

    def remove_bucket(self, bucket_name: str):
        pass

    def list_objects(self, bucket_name: str, recursive: bool):
        pass

    def bucket_exists(self, bucket_name: str):
        pass