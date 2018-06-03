from flask import Flask, render_template, request

import numpy as np
import pystache

import pymongo
from pymongo import MongoClient
import os
import sys

app = Flask(__name__, static_folder='static', static_url_path='')

mongo_url = os.getenv('mongo_url', None)
if(mongo_url == None):
    print('no url')
    sys.exit(0)

connection = pymongo.MongoClient(mongo_url)
db = connection['sc_lab']

USERS_COUNT = 10


@app.route('/')
def index():
    users = get_sorted_users()
    topics = get_sorted_topics()
    return render_template('index.html', users=users, topics=topics)


def get_sorted_users():
    users = db.comments.distinct("author")
    users.sort()
    return users


def get_sorted_topics():
    topics = db.comments.distinct("topic")
    topics.sort()
    return topics
