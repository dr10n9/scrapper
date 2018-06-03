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


@app.route('/user', methods = ['GET'])
def search_user():
    if request.method == 'GET':
        result = request.args
            print('result : ', result)
            username = result.get('value', type=str)
            print("username : ", username)

            commnets_count = get_comments_count_by_username(username)
            print("commnets_count : ", commnets_count)
            if (commnets_count == 0):
                return render_template("error.html", message = 'Wrong username')
            else:
                total_comments = get_comments_total_count()
                topics = get_topics_by_username(username)
		print('topics : ', topics)
		messages_in_topics = []
		for topic in topics:
                    messages_in_topics.append(get_comments_count_by_username_and_topic(username, topic))

		total_topics = len(topics)

		return render_template(
                        "user.html",
			coments_count = commnets_count,
			total_comments = total_comments,
			total_topics = total_topics,
			username = username,
			topics = topics,
			messages_in_topics = messages_in_topics)


@app.route('/topic', methods = ['GET'])
def search_topic():
	if request.method == 'GET':
		result = request.args
		print('result : ', result)
		topic = result.get('value', type=str)
		print("topic : ", topic)
		top = get_top_users_in_topic(topic)
		users = top['users']
		comments_counters = top['comments_counters']

		print('users : ', users)
		print('comments_counters : ', comments_counters)

		comments_total = get_comments_count_by_topic(topic)
		print('comments_total : ', comments_total)

		if (len(users) == 0):
			return render_template("error.html", message = 'Wrong topic name')
		
		
		return render_template(
			"topic.html",
			authors = users,
			counts = comments_counters,
			total = comments_total,
			topic = topic)


def get_topics_by_username(username):
    topics = db.comments.distinct( "topic", { "author": username} )
    return topics


def get_comments_count_by_username_and_topic(username, topic):
    comments = db.comments.find( {"author": username, "topic" : topic}).count()
    return comments


def get_comments_count_by_username(username):
    comments_count = db.comments.find( {"author": username }).count()
    return comments_count


def get_comments_count_by_topic(topic):
    topics_count = db.comments.find({"topic": topic}).count()
    return topics_count

def get_comments_total_count():
    comments_count = db.comments.find().count()
    return comments_count


def get_top_users_in_topic(topic, max_value=USERS_COUNT):
    comments = db.comments.aggregate(
        [
            {"$match": {"topic": topic}},
            { "$group": { "_id": "$author", "count": { "$sum": 1 } } },
            { "$sort": { "count": -1 } }
	])

    counter = 0
    users = []
    comments_counters = []
    for comment in comments:
        print('comment : ', comment)
	counter = counter + 1
        if (counter > max_value):
            break
        comments_counters.append(comment['count'])
        users.append(comment['_id'])

        return {
            "users": users,
            "comments_counters": comments_counters
        }

def get_sorted_users():
    users = db.comments.distinct("author")
    users.sort()
    return users


def get_sorted_topics():
    topics = db.comments.distinct("topic")
    topics.sort()
    return topics

if __name__ == "__main__":
    app.run(debug=True)
