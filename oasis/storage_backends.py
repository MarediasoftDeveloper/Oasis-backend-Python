from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings # Import settings to read STATICFILES_LOCATION/MEDIAFILES_LOCATION

class StaticStorage(S3Boto3Storage):
    # Set the location attribute using the value from settings.py
    location = settings.STATICFILES_LOCATION 
    # Optionally, set ACL here to override the global AWS_DEFAULT_ACL:
    # default_acl = 'public-read' 

class MediaStorage(S3Boto3Storage):
    location = settings.MEDIAFILES_LOCATION
    file_overwrite = settings.AWS_S3_FILE_OVERWRITE
    # default_acl = 'public-read'