from google.appengine.ext import db

class Task(db.Model):
    proposer = db.UserProperty()
    proposed = db.DateTimeProperty()
    uuid = db.StringProperty()
    title = db.StringProperty()
    blocks = db.SelfReferenceProperty()
    status = db.CategoryProperty()
    
class Command(db.Model):
    user    = db.UserProperty()
    created = db.DateTimeProperty()
    root    = db.StringProperty()
    args    = db.StringProperty()
    task    = db.ReferenceProperty(Task)
    
class Account(db.Model):
    user = db.UserProperty()
    task = db.ReferenceProperty(Task)
    
class Comment(db.Model):
    created = db.DateTimeProperty()
    task = db.ReferenceProperty(Task)
    body = db.StringProperty()