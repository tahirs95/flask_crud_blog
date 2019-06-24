#!/usr/bin/env python3
import os
from flask import Flask, render_template
from flask_restful import Resource, Api, reqparse
from flask_jwt import JWT, jwt_required
from resources.blog import Blog, BlogList
from flask_cors import CORS

app = Flask(__name__,static_folder='./static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "tahir"
api = Api(app)

CORS(app) 
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create')
def create():
    return render_template('create.html')

@app.route('/update')
def update():
    return render_template('update.html')

@app.route('/delete')
def delete():
    return render_template('delete.html')


# from db import db
# db.init_app(app)
@app.before_first_request
def create_tables():
    db.create_all()

api.add_resource(Blog, '/blog/<int:id>', '/blog')
api.add_resource(BlogList, '/blogs')

if __name__ == '__main__':
    from db import db
    db.init_app(app)
    app.run(port=5000, debug=True)
    # app.run(port=process.env.PORT, debug=True)
