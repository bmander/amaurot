from google.appengine.ext import db

class Task(db.Model):
    proposed = db.DateTimeProperty()
    started = db.DateTimeProperty()
    uuid = db.StringProperty()
    title = db.StringProperty()
    
class Command(db.Model):
    created = db.DateTimeProperty()
    root    = db.StringProperty()
    args    = db.StringProperty()
    task    = db.ReferenceProperty(Task)
    
class Account(db.Model):
    user = db.UserProperty()
    task = db.ReferenceProperty(Task)