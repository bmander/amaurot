from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from models import Task, Command, Account, Comment
import datetime
import uuid
from google.appengine.api import users
from google.appengine.ext import db

def get_or_init_account(user):
    account = Account.all().filter('user =', user).get()
    if account is None:
        account = Account(user=user)
        account.put()
    
    return account

def index(request):
    if 'offset' in request.GET:
        offset = int(request.GET['offset'])
    else:
        offset = 0
    
    # use Users API to get current user
    user = users.get_current_user()
    
    # if a user is logged in, redirect to their workstack page
    if not user:
      greeting = ("<a href=\"%s\">Sign in or register</a>." %
                  users.create_login_url("/"))
      return HttpResponse("<html><body><h1>Workstack</h1>%s</body></html>"%greeting)
    
    logout_url = users.create_logout_url("/")
    
    commands = Command.all().filter("user =", user).order('-created').fetch(50,offset=offset)
    account = get_or_init_account( user )
    todos = Task.all().filter("blocks =",account.task).filter("status =",db.Category("todo"))
    slushtasks = Task.all().filter("proposer =", user).filter("blocks =", None).filter("status =",db.Category("todo"))
    
    stack = []
    tt = account.task
    while tt is not None:
        stack.append( tt )
        tt = tt.blocks
        
    for i, task in enumerate(reversed(stack)):
        task.level = i

    return render_to_response( "index.html", {'account':account, 'commands':commands, 'user':user, 'logout_url':logout_url,'todos':todos,'stack':stack,'offset':offset+50,'slushtasks':slushtasks} )
    
def task(request, uuid):
    task = Task.all().filter("uuid =",uuid)[0]
    subtasks = Task.all().filter("blocks =",task)
    comments = Comment.all().filter("task =",task).order("-created")
    
    return render_to_response( "task.html", {'task':task,'subtasks':subtasks,'comments':comments} )

def push(command_args, account):
    title = command_args
    
    task = Task(proposer=account.user,
                proposed=datetime.datetime.now(),
                title=title,
                uuid=uuid.uuid1().hex,
                status=db.Category("underway"),
                blocks = account.task)
    task.put()

    account.task = task
    account.put()
    
    command = Command(user=account.user,
                      created=datetime.datetime.now(),
                      root="PUSH",
                      args=command_args,
                      task=task)
    command.put()
    
def pop(command_args, account):
    tobepopped = account.task
    tobepopped.status = db.Category("finished")
    tobepopped.put()
    
    account.task = account.task.blocks
    account.put()
    
    command = Command(user=account.user,
                      created=datetime.datetime.now(),
                      root="POP",
                      args=command_args,
                      task=tobepopped)
    command.put()
    
def todo(command_args, account):
    title = command_args
    
    task = Task(proposer=account.user,
                proposed=datetime.datetime.now(),
                title=title,
                uuid=uuid.uuid1().hex,
                status=db.Category("todo"),
                blocks = account.task)
    task.put()
    
    command = Command(user=account.user,
                      created=datetime.datetime.now(),
                      root="TODO",
                      args=command_args,
                      task=task)
    command.put()
    
def switch(command_args, account):
    
    uuid = command_args.strip()
    task = Task.all().filter("uuid =", uuid)[0]
    task.status = db.Category("underway")
    account.task = task
    account.put()
    
    command = Command(user=account.user,
                      created=datetime.datetime.now(),
                      root="SWITCH",
                      args=command_args,
                      task=task)
    command.put()
    
def comment(command_args, account):    
    cc = Comment(body = command_args,
                 task = account.task,
                 created = datetime.datetime.now())
    cc.put()
    
    command = Command(user=account.user,
                      created=datetime.datetime.now(),
                      root="COMMENT",
                      args=command_args,
                      task=account.task)
                      
    command.put()
    
def up(command_args, account):
    if not account.task:
        return
        
    toblock = account.task
    
    account.task = account.task.blocks
    account.put()
    
    command = Command(user=account.user,
                      created=datetime.datetime.now(),
                      root="UP",
                      args=command_args,
                      task=toblock)
    command.put()
    
def purpose(command_args, account):
    if not account.task:
        return
    
    uuids = command_args.strip().split()
    
    child_uuid = uuids[0]
    task_purpose = Task.all().filter("uuid =", child_uuid)[0]
    
    if len(uuids)==2:
        parent_uuid = uuids[1]
        task = Task.all().filter("uuid =", parent_uuid)[0]
    else:
        task = account.task
        
    task.blocks = task_purpose
    task.put()
        
    command = Command(user=account.user,
                      created=datetime.datetime.now(),
                      root="PURPOSE",
                      args=command_args,
                      task=task)
    command.put()
    
def slush(command_args, account):
    title = command_args
    
    task = Task(proposer=account.user,
                proposed=datetime.datetime.now(),
                title=title,
                uuid=uuid.uuid1().hex,
                status=db.Category("todo"),
                blocks = None)
    task.put()
    
    command = Command(user=account.user,
                      created=datetime.datetime.now(),
                      root="SLUSH",
                      args=command_args,
                      task=task)
    command.put()
    
commands = {'PUSH': push,
            'POP': pop,
            'TODO': todo,
            'SWITCH': switch,
            'COMMENT': comment,
            'UP':up,
            'PURPOSE':purpose,
            'SLUSH':slush,}

def command(request):
    command_content = request.POST['command'] if 'command' in request.POST else request.GET['command']
    command_root = command_content.split()[0].upper()
    command_args = command_content[len(command_root):].strip()
    
    account = get_or_init_account( users.get_current_user() )
    
    if command_root in commands:
        commands[command_root](command_args, account)
    else:
        comment( command_content, account )
    
    return HttpResponseRedirect("/")