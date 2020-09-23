from google.cloud import storage
import os
import uuid
from appConfig import DefaultConfig
from base64 import b64decode
import werkzeug.utils as wzu


class cloudstore_utils:
    def __init__(self):
        self.client = storage.Client.from_service_account_json(DefaultConfig.GOOGLE_BUCKET_JSON_PATH)
        self.bucket_name = DefaultConfig.GOOGLE_BUCKET_ID
        self.uploads_dir = os.path.join(os.getcwd(), DefaultConfig.TEMP_UPLOAD_FOLDER_NAME)
        self.ALLOWED_EXTENSIONS = DefaultConfig.ALLOWED_EXTENSIONS

    def upload_to_bucket(self, f):

    # Explicitly use service account credentials by specifying the private key
    # file.
        filename=str(uuid.uuid4())+"-"+f.filename
        full_file_path = os.path.join(self.uploads_dir,filename)
        f.save(full_file_path)
        #print(buckets = list(storage_client.list_buckets())
        bucket = self.client.get_bucket(self.bucket_name)
        blob = bucket.blob(filename)
        blob.upload_from_filename(full_file_path)
        os.remove(full_file_path)
        return blob.public_url
    
    def upload_to_bucket_b64List(self,images):
        urlList = []
        for image in images:
            decodedImage = b64decode(image['b64'])
            filename = wzu.secure_filename(str(uuid.uuid4())+'.'+image['file_ext'] )
            full_file_path = os.path.join(self.uploads_dir,filename)
            with open(full_file_path, 'wb') as f:
                f.write(decodedImage)
            bucket = self.client.get_bucket(self.bucket_name)
            blob = bucket.blob(filename)
            blob.upload_from_filename(full_file_path)
            os.remove(full_file_path)
            urlList.append(blob.public_url)
        return urlList
        
