import os

from minio import Minio

from persistence.object_storage.iobjectstorage_handler import IObjectStorageHandler
from utilities import logger_config

logger = logger_config.get_logger(__name__)


class MinioHandler(IObjectStorageHandler):

    def __init__(self, config):
        self.minio_client = self._initialize_client(config)

    def _initialize_client(self, config):
        return Minio(
            config['url'],
            access_key=config['access_key'],
            secret_key=config['secret_key'],
            secure=False
        )

    def bucket_exists(self, bucket_name: str):
        try:
            return self.minio_client.bucket_exists(bucket_name)
        except Exception as e:
            logger.error(f"Minio make bucket exception: {str(e)}")

    def make_bucket(self, bucket_name: str, location: str):
        try:
            self.minio_client.make_bucket(bucket_name, location)
        except Exception as e:
            logger.error(f"Minio make bucket exception: {str(e)}")

    def upload_file(self, bucket_name: str, object_name: str, file_path: str):
        logger.info(f"Upload file: {file_path}")
        success = None
        try:
            self.minio_client.fput_object(bucket_name, object_name, file_path)
            success = True
        except Exception as e:
            logger.error(f"Minio upload exception occured: {str(e)}")
        finally:
            return success

    def download_file(self, bucket_name: str, object_name: str, storage_path: str):
        logger.info(f"Download object: {object_name} - stored in: {os.path.join(storage_path, object_name)}")
        success = None
        try:
            self.minio_client.fget_object(bucket_name, object_name, os.path.join(storage_path, object_name))
            success = True
        except Exception as e:
            logger.error(f"Minio download exception occured: {str(e)}")
        finally:
            return success

    def delete_file(self, bucket_name: str, object_name: str):
        logger.info(f"Delete file: {object_name}")
        try:
            self.minio_client.remove_object(bucket_name, object_name)
        except Exception as e:
            logger.error(f"Minio delete file exception occured: {str(e)}")

    def delete_files(self, bucket_name: str, files: list):
        logger.info(f"Delete files: {files}")
        try:
            self.minio_client.remove_objects(bucket_name, files)
        except Exception as e:
            logger.error(f"Minio delete files exception occured: {str(e)}")

    def remove_bucket(self, bucket_name: str):
        logger.info(f"Remove bucket: {bucket_name}...")
        try:
            self.minio_client.remove_bucket(bucket_name)
        except Exception as e:
            logger.error(f"Minio remove bucket exception occured: {str(e)}")

    def list_objects(self, bucket_name: str, recursive: bool = True):
        logger.info(f"List objects in bucket: {bucket_name}")
        try:
            objects = self.minio_client.list_objects(bucket_name, recursive=recursive)
            return [obj.object_name for obj in objects]
        except Exception as e:
            logger.error(f"Minio list exception occured: {str(e)}")
