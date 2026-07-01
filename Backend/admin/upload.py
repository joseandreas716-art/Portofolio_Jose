import os
import uuid
import logging
from flask import Blueprint, current_app
from cloudinary.uploader import upload as cloudinary_upload
from cloudinary.uploader import destroy as cloudinary_destroy
from cloudinary.utils import cloudinary_url
from cloudinary import config as cloudinary_config

logger = logging.getLogger(__name__)

upload_bp = Blueprint('upload', __name__)

class CloudinaryService:
    def __init__(self):
        self.cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME')
        self.api_key = os.getenv('CLOUDINARY_API_KEY')
        self.api_secret = os.getenv('CLOUDINARY_API_SECRET')
        
        if self.cloud_name and self.api_key and self.api_secret:
            cloudinary_config(
                cloud_name=self.cloud_name,
                api_key=self.api_key,
                api_secret=self.api_secret,
                secure=True
            )
            self.use_cloudinary = True
        else:
            self.use_cloudinary = False

    def upload_image(self, file_stream, filename, folder='portfolio'):
        if not file_stream:
            raise ValueError('No file stream provided for upload')

        if self.use_cloudinary:
            try:
                name_without_ext, _ = os.path.splitext(filename)
                unique_public_id = f"{name_without_ext}_{uuid.uuid4().hex[:8]}"
                
                response = cloudinary_upload(
                    file_stream,
                    public_id=unique_public_id,
                    folder=folder,
                    overwrite=True,
                    resource_type='image',
                )
                return response.get('secure_url')
            except Exception as error:
                raise RuntimeError(f'Cloudinary upload failed: {error}')
        else:
            # Fallback to local storage
            try:
                # Store uploads in Frontend/static/uploads or Frontend/uploads
                # Wait, in Flask, if static_folder is 'Frontend', we can store inside Frontend/uploads/
                upload_dir = os.path.join(current_app.root_path, 'Frontend', 'uploads', folder)
                os.makedirs(upload_dir, exist_ok=True)
                
                name_without_ext, ext = os.path.splitext(filename)
                unique_filename = f"{name_without_ext}_{uuid.uuid4().hex[:8]}{ext}"
                
                file_path = os.path.join(upload_dir, unique_filename)
                with open(file_path, 'wb') as f:
                    file_stream.seek(0)
                    f.write(file_stream.read())
                    file_stream.seek(0)
                
                # Public URL path: /Frontend/uploads/folder/filename
                return f'/Frontend/uploads/{folder}/{unique_filename}'
            except Exception as error:
                raise RuntimeError(f'Local upload fallback failed: {error}')

    def delete_image(self, image_url):
        if not image_url:
            return False
            
        if self.use_cloudinary and 'res.cloudinary.com' in image_url:
            try:
                parts = image_url.split('/upload/')
                if len(parts) > 1:
                    path_after_upload = parts[1]
                    subparts = path_after_upload.split('/')
                    if subparts[0].startswith('v') and subparts[0][1:].isdigit():
                        subparts = subparts[1:]
                    
                    public_id_with_ext = '/'.join(subparts)
                    public_id, _ = os.path.splitext(public_id_with_ext)
                    
                    response = cloudinary_destroy(public_id)
                    return response.get('result') == 'ok'
            except Exception as error:
                logger.error(f'Cloudinary image deletion failed: {error}')
                return False
        else:
            # Fallback to local file deletion
            try:
                if image_url.startswith('/Frontend/'):
                    rel_path = image_url.lstrip('/')
                    file_path = os.path.join(current_app.root_path, rel_path)
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        return True
            except Exception as error:
                logger.error(f'Local image deletion failed: {error}')
                return False
        return False
