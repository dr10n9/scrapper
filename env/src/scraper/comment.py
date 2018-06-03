class Comment():
    def __init__(self, author, text, date, topic):
        self.author = author
        self.text = text
        self.date = date
        self.topic = topic

    def to_string(self):
        return 'author : ' + self.author + '\n' + \
            'text : ' + self.text + '\n' + \
            'date : ' + self.date + '\n' + \
            'topic : ' + self.topic
