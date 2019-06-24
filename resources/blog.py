import sqlite3
from flask import Flask, jsonify, request, render_template, send_file
from flask_restful import Resource, Api, reqparse
from models.blog import BlogModel
import json
import os
import requests
import boto3
import logging
from botocore.exceptions import ClientError
from boto3.s3.transfer import S3Transfer
from sightengine.client import SightengineClient
from botocore.client import Config



ACCESS_KEY_ID = ''
ACCESS_SECRET_KEY = ''
BUCKET_NAME = ''


def image_check(image_url):
    client = SightengineClient('', '')
    output = client.check('nudity','offensive').set_url(image_url)
    safe = output['nudity']['safe']
    return safe

class Blog(Resource):
    def get(self, id):
        blog= BlogModel.find_by_id(id)
        if blog:
            return blog.json()
        return {"message":"Item not found"}, 404

    def post(self):

        f = request.files['file']
        title = request.form["title"]
        content = request.form["content"]
        img_name = request.form["img_name"]
        
        s3 = boto3.resource(
        's3',
        aws_access_key_id=ACCESS_KEY_ID,
        aws_secret_access_key=ACCESS_SECRET_KEY,
        config=Config(signature_version='s3v4'))

        # # Image Uploaded
        s3.Bucket(BUCKET_NAME).put_object(Key=img_name, Body=f, ACL='public-read')
        img_url = 'https://jkhatter-flask.s3-us-west-2.amazonaws.com/%s' %(img_name)
        print(img_url)

        safe = image_check(img_url)

        if safe > 0.50:
            blog = BlogModel(title, content, img_name, img_url)
            try:
                blog.insert_update()
            except:
                return({"message":"An error occurred in inserting the item."}), 500 #internal server error
            return blog.json(), 201
        else:
            return({"message":"Image contains nudity content."}), 400

    def delete(self, id):
        blog = BlogModel.find_by_id(id)
        s3 = boto3.resource(
            's3',
            aws_access_key_id=ACCESS_KEY_ID,
            aws_secret_access_key=ACCESS_SECRET_KEY,
            config=Config(signature_version='s3v4')
        )

        # This will delete the old image
        obj = s3.Object(BUCKET_NAME, blog.img_name)
        obj.delete()
        print("Delete done")
        if blog:
            blog.delete()
            return {"message":"Item deleted"}
        else:
            return({"message":"Item not found."})

    def put(self, id):
        f = request.files['file']
        title = request.form["title"]
        content = request.form["content"]
        img_name = request.form["img_name"]
        blog = BlogModel.find_by_id(id)
        s3 = boto3.resource(
            's3',
            aws_access_key_id=ACCESS_KEY_ID,
            aws_secret_access_key=ACCESS_SECRET_KEY,
            config=Config(signature_version='s3v4')
        )

        # This will delete the old image
        obj = s3.Object(BUCKET_NAME, img_name)
        obj.delete()
        print("Delete done")

        # This will upload the new image
        s3.Bucket(BUCKET_NAME).put_object(Key=img_name, Body=f, ACL='public-read')
        img_url = 'https://jkhatter-flask.s3-us-west-2.amazonaws.com/%s' %(img_name)
        print (img_url)
        

        safe = image_check(img_url)
        if safe > 0.50:
            if blog is None:
                blog = BlogModel(title, content, img_name, img_url)
            else:
                blog.title = title
                blog.content = content
                blog.img_name = img_name
                blog.img_url = img_url
            blog.insert_update()
            return blog.json()
        else:
            return({"message":"Image contains nudity content."}), 400

class BlogList(Resource):
    def get(self):
        items = list(map(lambda x: x.json(), BlogModel.query.all()))
        return items

def downloadImage(url,name):

    response = requests.get(url)
    filename=name.replace(" ", "_")
    file = filename+".jpg"

    if response.status_code == 200:
        with open(file, 'wb') as f:
            f.write(response.content)
    return file

def uploadImagesToS3(file,name):
    bucket_name = "jkhatter-flask"
    key=name.replace(" ", "_")


    client = boto3.client('s3')
    transfer = S3Transfer(client)

    try:
        transfer.upload_file(file, bucket_name, key)
        response = client.put_object_acl(ACL='public-read', Bucket=bucket_name, Key=key)
    except ClientError as e:
        logging.error(e)
        return False
    os.remove(file)
    return key

def fetchImageFromS3(key):
    bucket_name = "jkhatter-flask"
    location = boto3.client('s3').get_bucket_location(Bucket=bucket_name)['LocationConstraint']
    url = "https://s3-%s.amazonaws.com/%s/%s" % (location, bucket_name, key)
    return url