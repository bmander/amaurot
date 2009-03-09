from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from models import Task

def index(request):
    tasks = Task.all()
    
    return render_to_response( "index.html", {'tasks':tasks} )

def new_task(argv):
    title = " ".join(argv[1:])
    
    task = Task(title=title)
    task.put()

commands = {'PUSH': new_task}

def command(request):
    argv = request.POST['command'].split()
    
    if argv[0].upper() in commands:
        commands[argv[0].upper()](argv)
    
    return HttpResponseRedirect("/")