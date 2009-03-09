from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from models import Task, Command
import datetime

def index(request):
    commands = Command.all().order('-created')
    
    return render_to_response( "index.html", {'commands':commands} )

def push(command_args):
    title = command_args
    
    task = Task(title=title)
    task.put()
    
    command = Command(created=datetime.datetime.now(),
                      root="PUSH",
                      args=command_args,
                      task=task)
    command.put()

commands = {'PUSH': push}

def command(request):
    command_content = request.POST['command']
    command_root = command_content.split()[0].upper()
    command_args = command_content[len(command_root):].strip()
    
    if command_root in commands:
        commands[command_root](command_args)
    
    return HttpResponseRedirect("/")