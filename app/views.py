from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from models import Task, Command, Account
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
    # use Users API to get current user
    user = users.get_current_user()
    
    # if a user is logged in, redirect to their workstack page
    if not user:
      greeting = ("<a href=\"%s\">Sign in or register</a>." %
                  users.create_login_url("/"))
      return HttpResponse("<html><body><h1>Workstack</h1>%s</body></html>"%greeting)
    
    logout_url = users.create_logout_url("/")
    
    commands = Command.all().filter("user =", user).order('-created')
    account = get_or_init_account( user )
    
    return render_to_response( "index.html", {'account':account, 'commands':commands, 'user':user, 'logout_url':logout_url} )
    
def task(request, uuid):
    task = Task.all().filter("uuid =",uuid)[0]
    subtasks = Task.all().filter("blocks =",task)
    
    return render_to_response( "task.html", {'task':task,'subtasks':subtasks} )

def push(command_args, account):
    title = command_args
    
    task = Task(proposer=account.user,
                proposed=datetime.datetime.now(),
                title=title,
                uuid=uuid.uuid1().hex,
                status=db.Category("underway"))
    task.blocks = account.task
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
                status=db.Category("todo"))
    task.blocks = account.task
    task.put()
    
    command = Command(user=account.user,
                      created=datetime.datetime.now(),
                      root="TODO",
                      args=command_args,
                      task=task)
    command.put()
    

commands = {'PUSH': push,
            'POP': pop,
            'TODO': todo}

def command(request):
    command_content = request.POST['command']
    command_root = command_content.split()[0].upper()
    command_args = command_content[len(command_root):].strip()
    
    account = get_or_init_account( users.get_current_user() )
    
    if command_root in commands:
        commands[command_root](command_args, account)
    
    return HttpResponseRedirect("/")