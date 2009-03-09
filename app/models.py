from google.appengine.ext import db

class Task(db.Model):
    proposed = db.DateTimeProperty()
    started = db.DateTimeProperty()
    title = db.StringProperty()
    
class Command(db.Model):
    created = db.DateTimeProperty()
    root    = db.StringProperty()
    args    = db.StringProperty()
    task    = db.ReferenceProperty(Task)