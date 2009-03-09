from google.appengine.ext import db

class Task(db.Model):
    title = db.StringProperty()