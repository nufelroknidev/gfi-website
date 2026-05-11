from storages.backends.s3boto3 import S3Boto3Storage


class StaticS3Storage(S3Boto3Storage):
    """Static files — stored under static/ prefix in S3."""
    location = 'static'


class MediaS3Storage(S3Boto3Storage):
    """User-uploaded media — stored under media/ prefix in S3."""
    location = 'media'
