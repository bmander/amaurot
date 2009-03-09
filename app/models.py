from google.appengine.ext import db

class Task(db.Model):
    proposer = db.UserProperty()
    proposed = db.DateTimeProperty()
    started = db.DateTimeProperty()
    completed = db.DateTimeProperty()
    uuid = db.StringProperty()
    title = db.StringProperty()
    blocks = db.SelfReferenceProperty()
    
class Command(db.Model):
    user    = db.UserProperty()
    created = db.DateTimeProperty()
    root    = db.StringProperty()
    args    = db.StringProperty()
    task    = db.ReferenceProperty(Task)
    
class Account(db.Model):
    user = db.UserProperty()
    task = db.ReferenceProperty(Task)