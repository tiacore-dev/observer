from loguru import logger
import aioboto3
from botocore.exceptions import ClientError
from config import Settings

settings = Settings()


class AsyncS3Manager:
    endpoint_url = settings.ENDPOINT_URL
    region_name = settings.REGION_NAME
    aws_access_key_id = settings.AWS_ACCESS_KEY_ID
    aws_secret_access_key = settings.AWS_SECRET_ACCESS_KEY
    bucket_name = settings.BUCKET_NAME
    bucket_folder = "web_app"

    def _get_session(self):
        return aioboto3.Session()

    def _build_path(self, chat_id: int, filename: str) -> str:
        return f"{self.bucket_folder}/{chat_id}/{filename}"

    async def upload_bytes(self, file_bytes: bytes, chat_id: int, filename: str):
        key = self._build_path(chat_id, filename)
        session = self._get_session()
        async with session.client(
            "s3",
            endpoint_url=self.endpoint_url,
            region_name=self.region_name,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
        ) as s3:
            try:
                await s3.put_object(
                    Bucket=self.bucket_name,
                    Key=key,
                    Body=file_bytes,
                    ACL="private"
                )
                logger.info(f"✅ Файл загружен: {key}")
                return key
            except ClientError as e:
                logger.error(f"Ошибка загрузки: {e}")
                raise

    async def generate_presigned_url(self, key, expiration=3600):
        session = self._get_session()
        async with session.client(
            "s3",
            endpoint_url=self.endpoint_url,
            region_name=self.region_name,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
        ) as s3:
            try:
                return await s3.generate_presigned_url(
                    ClientMethod='get_object',
                    Params={"Bucket": self.bucket_name, "Key": key},
                    ExpiresIn=expiration
                )
            except ClientError as e:
                logger.error(f"Ошибка при генерации ссылки: {e}")
                return None

    async def list_chat_files(self, chat_id: int) -> list[str]:
        prefix = f"{self.bucket_folder}/{chat_id}/"
        session = self._get_session()
        async with session.client(
            "s3",
            endpoint_url=self.endpoint_url,
            region_name=self.region_name,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
        ) as s3:
            try:
                response = await s3.list_objects_v2(
                    Bucket=self.bucket_name,
                    Prefix=prefix
                )
                return [obj["Key"] for obj in response.get("Contents", [])]
            except ClientError as e:
                logger.error(f"Ошибка при получении списка файлов: {e}")
                return []
