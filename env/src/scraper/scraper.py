import scrapy
import re
from bs4 import BeautifulSoup
import pymongo
from pymongo import MongoClient
import os
import sys
from urllib.parse import urlparse
from comment import Comment

import json
from pprint import pprint


mongo_url = os.getenv('lab2_url', None)
if(mongo_url == None):
    print('no url')
    sys.exit(0)

print(mongo_url)

connection = pymongo.MongoClient(mongo_url)
db = connection['sc_lab']


INPUT = 'input.json'


class Spider(scrapy.Spider):

    with open(INPUT) as f:
        data = json.load(f)

    try:
        name = data['spider_name']
        comment_per_page = data['comments_per_page']
        max_comments = data['max_comments']
        posts_key = data['keys']['posts']
        topic_key = data['keys']['topic']
        next_page_key = data['next_page_link']

        post_text_element = data['post_keys']['text']['element']
        post_text_class = data['post_keys']['text']['class']
        post_answer_element = data['post_keys']['answer']['element']
        post_answer_class = data['post_keys']['answer']['class']
        post_author_element = data['post_keys']['author']['element']
        post_author_class = data['post_keys']['author']['class']
        post_date_element = data['post_keys']['date']['element']
        post_date_class = data['post_keys']['date']['class']
        thread_key = data['thread_key']

    except:
       print("\tERROR: data.json is wrong. Please fill all default fields")
       sys.exit(0)

    try:
       forum_urls = data['forum_urls']

    except:
       forum_urls = None

    try:
       urls = data['concrete_urls']

    except:
       urls = None

    if urls == None and forum_urls == None:
       print('\tERROR: concrete_urls and forum_urls in data.json is empty. Please fill all default fields')
       sys.exit(0)

    url_counter = 0
    current_page = 1
    total = 0


    def start_requests(self):
        for url in self.urls:
            yield scrapy.Request(url=url, callback=self.parse)

        for forum in self.forum_urls:
            yield scrapy.Request(url=forum, callback=self.parse_forum)


    def parse_forum(self, response):
        domain = self.response_get_domain(response)
        links = reponse.xpath(self.thread_key).extract()

        for link in links:
            href = "{domain}{link}".format(domain=domain, link=link)
            yield scrapy.Request(url=href, callback=self.parse)


    def parse(self, response):
        try:
            posts = response.xpath(self.posts_key).extract()
        except:
            print('post scrap fail')
            return None

        try:
            topic = response.xpath(self.topic_key).extract()
        except:
            topic = 'unknown'

        for post in posts:
            self.url_counter += 1
            self.total_counter += 1

            comment = self.parse_post(post, topic)

            print()
            print(comment.to_string())
            self.db_save_comment(comment)

            if self.total >= self.max_counter:
                print('Completed')
                sys.exit(0)

            if self.url_counter >= self.comments_per_page:
                self.url_counter = 0
                link = self.get_next_page_link(response)
                return scrapy.Request(url=link, callback=self.parse)


    def parse_post(self, post, topic):
        print('url counter: ', self.url_counter)
        soup = BeautifulSoup(post, 'html.parser')

        text = soup.findAll(self.post_text_element, {'class': self.post_text_class})
        answer = soup.findAll(self.post_answer_element, {'class': self.post_answer_class})
        author = soup.findAll(self.post_author_element, {'class': self.post_author_class})
        date = soup.findAll(self.post_date_element, {'class': self.post_date_class})

        author = author[0].text
        text = text[0].text
        date = date[0].text
        try:
            to_delete = answer[0].text
            text = text[len(to_delete):]
        except:
            print(None)

        author = author.strip()
        text = text.strip()

        return Comment(author, text, date, topic)


    def get_next_page_link(self, response):
        domain = self.response_get_domain(response)
        href = response.xpath(self.next_page_key).extract_first()
        if href == None:
            return None

        next_page_link = domain + href
        return next_page_link


    def db_save_comment(self, comment):
        data = {
            'author' : comment.author,
            'text' : comment.text,
            'date' : comment.date,
            'topic' : comment.topic
        }
        return db.comments.update(data, data, upsert='True')


    def response_get_domain(self, response):
        href = str(response)
        href = href[4:]
        href = href[:-1]
        href = href.strip()
        parsed = urlparse(href)
        domain = '{uri.scheme}://{uri.netloc}'.format(uri=parsed)
        return domain
