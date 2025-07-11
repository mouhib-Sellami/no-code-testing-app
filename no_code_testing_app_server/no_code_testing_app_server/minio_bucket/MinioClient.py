import os
import io
from minio import Minio
from no_code_testing_app_server.patterns.Singleton import singleton
from datetime import timedelta
from minio.error import S3Error
import tempfile


@singleton
class MinioClient():
    def __init__(self):
        self.client = Minio(os.getenv("MINIO_HOST"),
                            access_key=os.getenv("ACCESS_KEY"),
                            secret_key=os.getenv("SECRET_KEY"),
                            secure=False
                            )
        self.bucket = os.getenv("MINIO_DEFAULT_BUCKETS")

    def find_or_create_bucket(self):
        found = self.client.bucket_exists(self.bucket)
        if not found:
            self.client.make_bucket(self.bucket)
            print("Created bucket", self.bucket)
        else:
            print("Bucket", self.bucket, "already exists")

    def create_folder(self, folder_name):
        self.client.put_object(self.bucket, str(folder_name) +
                               '/', data=io.BytesIO(b''), length=0)

    def get_public_link(self, file):
        return self.client.get_presigned_url(
            'GET', self.bucket, file, expires=timedelta(days=7000))

    def upload_single(self, file, folder_name):
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            try:
                for chunk in file.chunks():
                    temp_file.write(chunk)
                temp_file.close()
                self.client.fput_object(
                    self.bucket,
                    str(folder_name)+"/" + file.name,
                    temp_file.name,
                    content_type=file.content_type,
                )
            except S3Error as e:
                print(e)
                raise e
            finally:
                os.remove(temp_file.name)
                
    def upload_single(self, file, folder_name):
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            try:
                self.client.fput_object(
                    self.bucket,
                    str(folder_name)+"/" + file.name,
                    file.name,
                    content_type=file.content_type,
                )
            except S3Error as e:
                print(e)
                raise e
            finally:
                os.remove(temp_file.name)