import cloudinary
import cloudinary.uploader
import cloudinary.api
from flask import request, jsonify



class Uploader:
    def __init__(self):
        self.url = None
    def upload(self,file,app):
        app.logger.info('in upload route')
        cloudinary.config(cloud_name= 'cafeandwifi',
                          api_key= '568799749678543',
                          api_secret= 'z8OAdxtZIKUDWgI3-7Aajxs5NI0'
                          )
        upload_result = None
        if request.method == 'POST':
            file_to_upload = file
            app.logger.info('%s file_to_upload', file_to_upload)
            if file_to_upload:
                upload_result = cloudinary.uploader.upload(file_to_upload)
                app.logger.info(upload_result)
                self.url = upload_result['secure_url']
                return jsonify(upload_result)
