from flask import Flask, render_templates, request

import numpy as np
import pystache

import pymongo
from pymongo import MongoClient
import os
import sys

app = Flask(__name__, static_folder='static', static_url_path='')

mongo_url = os.getenv('lab2_url', None)
if(mongo_url == None):
    print('no url')
    sys.exit(0)

connection = pymongo.MongoClient(mongo_url)
db = connection['sc_lab']

USERS_COUNT = 10


@app.route('/')
