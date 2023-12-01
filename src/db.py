from flask_sqlalchemy import SQLAlchemy
import base64
import boto3
import datetime
import io
from io import BytesIO
from mimetypes import guess_type, guess_extension
import os
from PIL import Image
import random
import re
import string

db = SQLAlchemy()

EXTENSIONS = ["png", "gif", "jpeg", "jpg"]
BASE_DIR = os.getcwd()
S3_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME")
S3_BASE_URL = f"https://{S3_BUCKET_NAME}.s3.us-east-1.amazonaws.com"

class Asset(db.Model):
    """
    Asset Model
    """
    __tablename__ = "asset"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    base_url = db.Column(db.String, nullable=False)
    salt = db.Column(db.String, nullable=False)
    extension = db.Column(db.String, nullable=False)
    width = db.Column(db.Integer, nullable=False)
    height = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)

    def __init__(self, **kwargs):
        """
        Initializes an asset object
        """
        self.create(kwargs.get("image_data"))

    def serialize(self):
        """
        Serializes an Asset Object
        """
        return {
            "url": f"{self.base_url}/{self.salt}.{self.extension}",
            "created_at": str(self.created_at)
        }
    
    def create(self, image_data):
        """
        Given an image in base 64 encoding, does the following
        1. Rejects the image if it is not a supported file type
        2. Generate random string for the image filename
        3. Decodes the image and attempts to upload it to AWS
        """

        try:
            ext = guess_extension(guess_type(image_data)[0])[1:]

            if ext not in EXTENSIONS:
                raise Exception(f"extension ext is not valid")
            
            salt = "".join(
                random.SystemRandom().choice(
                    string.ascii_uppercase + string.digits
                )
                for _ in range(16)
                    
            )

            img_str = re.sub("^data:image/.+;base64,", "", image_data)
            img_data= base64.b64decode(img_str)
            img = Image.open(BytesIO(img_data))

            self.base_url = S3_BASE_URL
            self.salt = salt
            self.extension = ext
            self.width = img.width
            self.height = img.height
            self.created_at = datetime.datetime.now()

            img_filename = f"{self.salt}.{self.extension}"

            self.upload(img, img_filename)

        except Exception as e:
            print("Error when creating image: {e}")

    def upload(self, img, img_filename):
        """
        Attempts to upload the image into the specified S3 bucket.
        """
        try:
            #save image in temporary location
            img_temp_loc = f"{BASE_DIR}/{img_filename}"
            img.save(img_temp_loc)

            #upload image into S3 bucket
            s3_client = boto3.client("s3")
            s3_client.upload_file(img_temp_loc, S3_BUCKET_NAME, img_filename)

            s3_resource = boto3.resource("s3")
            object_acl = s3_resource.ObjectAcl(S3_BUCKET_NAME, img_filename)
            object_acl.put(ACL = "public-read")

            #remove image from temp location
            os.remove(img_temp_loc)

        except Exception as e:
            print("Error when uploading image: {e}")
    



class Day(db.Model):
    """
    Day Model
    """
    __tablename__ = "day"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.String, nullable=False)
    overall_rating = db.Column(db.Integer, nullable=False)
    posts = db.relationship("Post")

    def __init__(self, **kwargs):
        """
        Initialize a Post object
        """
        self.date = kwargs.get("date", "")
        self.overall_rating = kwargs.get("overall_rating", "")

    def serialize(self):
         """
         Serializes a Day object.
         """
         return {
              "id": self.id,
              "date": self.date,
              "overall_rating": self.overall_rating,
              "posts": [p.serialize() for p in self.posts],
         }
    
    def update_rating(self, new_rating):
        self.overall_rating = new_rating


class Post(db.Model):
    """
    Post Model
    """
    __tablename__ = "post"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    location = db.Column(db.String, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    text = db.Column(db.String)
    day_id = db.Column(db.Integer, db.ForeignKey("day.id"), nullable=False)
    pic = db.Column(db.LargeBinary, nullable=False)
    
    def __init__(self, **kwargs):
        """
        Initialize a Post object
        """
        self.location = kwargs.get("location", "")
        self.rating = kwargs.get("rating", "")
        self.text = kwargs.get("text", "")
        self.day_id = kwargs.get("day_id")
        self.pic = kwargs.get("pic")

    def serialize(self):
         """
         Serializes a Post object.
         """
         return {
              "id": self.id,
              "location": self.location,
              "rating": self.rating,
              "text": self.text, 
              "day_id": self.day_id, 
              "pic": self.pic
         }