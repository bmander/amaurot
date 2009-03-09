from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from models import Task

def index(request):
    tasks = Task.all()
    
    return render_to_response( "index.html", {'tasks':tasks} )

def new_task(command_args):
    title = command_args
    
    task = Task(title=title)
    task.put()

commands = {'PUSH': new_task}

def command(request):
    command_content = request.POST['command']
    command_root = command_content.split()[0].upper()
    command_args = command_content[len(command_root):].strip()
    
    if command_root in commands:
        commands[command_root](command_args)
    
    return HttpResponseRedirect("/")