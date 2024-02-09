from django.shortcuts import render, redirect
from django.contrib import messages

# Restrict User/////
from django.contrib.auth.decorators import login_required
# ////////////////////

# imported for if user is not the right user //
from django.http import HttpResponse
#  ////////////////////////////////

# imported for the user registration
# from django.contrib.auth.forms import UserCreationForm
# ..................................

# from django.contrib.auth.models import User
# and there wasn't User after Message initially
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from .models import Room, Topic, Message, User
from .forms import RoomForm, UserForm, MyUserCreationForm

# Create your views here.

# rooms = [
#     {"id" : 1, "name" : "Lets learn python!"},
#     {"id" : 2, "name" : "Design with me"},
#     {"id" : 3, "name" : "Frontend developers"},
# ]


def loginPage(request):

    # for the register
    page = 'login'
    # /////////////

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        email = request.POST.get('email').lower()
        password = request.POST.get('password')
        
        #use try: to make sure the user actually exists ///
        try:
            #import models user at the top  ///
            user = User.objects.get(email=email)
            # user = User.objects.get(username="tina")
        except:
            #import messages at top ////
            messages.error(request,'User does not exist')  

            #if the user exists ///
            #import authenticate, login and login out method at the top ///
        user = authenticate(request, email=email, password=password)
        # user = authenticate(request, username="tina", password="12345678qwertyui")

        if user is not None:
            login(request, user)
            return redirect('home')   
        else:
            messages.error(request,'User OR Password does not exist')     
     
    #  for the register
    context = {'page':page}
    # //////////////
    return render(request, "home/login_register.html", context)

def logoutUser(request):
    logout(request)
    return redirect('home')

# for register
def registerPage(request):
    form = MyUserCreationForm()

    if request.method == 'POST':
        # the request.POST is for the password or credentials the user submitted //
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
        # Let's customize user submission //
           user = form.save(commit=False) 
        # the commit=False is so that we can actually access the user right away,
        # this is because incase the user added in some UPPERCASE, we want to make sure it's LowerCase automatically or clean it with lowercase
           user.username = user.username.lower()
           user.save() 
        # Log the user in and send them to home page ............      
           login(request, user)  
           return redirect('home')
        else:
            messages.error(request, 'An error occured during registration')
    return render(request,"home/login_register.html", {'form': form})
# //////////

def homePage(request):
    q = request.GET.get("q")  if request.GET.get("q") != None else ""
    # rooms = Room.objects.filter(topic__name__icontains = q) 

    #remember to import Q at the top .........///////////
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )
    # the [0:5] is to limit the topics to the top 5
    topics = Topic.objects.all()[0:5] 

    room_count = rooms.count()

    # for recent activities
    # room_messages =Message.objects.all() 
    room_messages =Message.objects.filter(Q(room__topic__name__icontains=q)) 
    # the filter is because, if u click on javascript, only javascript with its recent activaties on it will be
    # displayed, instead of with the activities on other Topics
    # ...................

    context = {'rooms': rooms, 'topics':topics, 'room_count': room_count, 'room_messages' : room_messages}
    return render(request, 'home/index.html', context)

def roomPage(request, pk):
    room = Room.objects.get(id=pk)   
    # for the comments in a room
    room_messages = room.message_set.all()
    # .order_by("-created") means newer messages will come first
    # message_set.all() means, give us all the messages that are related to this room,
    # the message is from the modal name Message, but now not in capital letter
    # ........................ 
    # participants.all() is due to ManyToMany relationships
    participants = room.participants.all()

    if request.method == "POST":
        message  = Message.objects.create(
             user = request.user,
             room = room,
             body = request.POST.get("body")
            #  this "body" is from the input tag with the name "body" in room.html
        )
        # this is to automatically .add() 0r .remove() a user as a participants when the user comments in a room
        room.participants.add(request.user)
        return redirect('room', pk = room.id)

    context = {'room' : room, 'room_messages' : room_messages, 'participants' : participants}
    return render(request, 'home/room.html', context)

# def roomPage(request, pk):
#     room = None
#     for i in rooms:
#         if i ['id'] == int(pk):
#             room = i
#     context = {'room': room}        
#     return render(request, 'home/room.html', context)

def userProfile(request, pk):
    user = User.objects.get(id = pk)
    # get all the users room
    rooms = user.room_set.all()
    # ,,,,,...........//
    topics = Topic.objects.all()
    room_messages = user.message_set.all()
    context = {"user" : user, "rooms": rooms, "room_messages" : room_messages, "topics": topics}
    return render(request, 'home/profile.html', context)

# we want this room to be restricted to certain user 
@login_required(login_url = 'login')
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()

    if request.method == "POST":
        topic_name = request.POST.get('topic')
        # get_or_create enables a user to create a new topic that was not initially created in the database .../
        topic, created = Topic.objects.get_or_create(name = topic_name)

        Room.objects.create(
            host = request.user,
            topic = topic,
            name = request.POST.get('name'),
            description = request.POST.get('description'),
        )
        # form = RoomForm(request.POST)
        # if form.is_valid():
        #     room = form.save(commit= False)
        #     room.host = request.user
        #     room.save()
            
            # form.save()
            #dont forget to redirect at the top/////////
        return redirect("home")

    context = {"form":form, "topics" : topics}
    return render(request, "home/room_form.html", context)


# Only authenticated user can update room
@login_required(login_url = 'login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()

    # if user is not the right user or owner here
    if request.user != room.host:
        return HttpResponse('You are not allowed here!!')
    # ////////

    if request.method == "POST":
        topic_name = request.POST.get('topic')
        # get_or_create enables a user to create a new topic that was not initially created in the database .../
        topic, created = Topic.objects.get_or_create(name = topic_name)
        room.name = request.POST.get('name')
        # room.topic = topic is because a user can create a new topic .......//
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()

        # form = RoomForm(request.POST, instance=room)
        # if form.is_valid():
        #     form.save()
        #     dont forget to redirect at the top
        return redirect("home")


    context = {"form":form, "topics" : topics, "room" : room}
    return render(request, "home/room_form.html", context)

# Only authenticated user can delete room
@login_required(login_url = 'login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

      # if user is not the right user or owner here
    if request.user != room.host:
        return HttpResponse('You are not allowed here!!')
    # ////////
    
    if request.method == "POST":
        room.delete()
        return redirect("home")
    return render(request, "home/delete.html", {"obj":room})

# Only authenticated user can delete his/her message
@login_required(login_url = 'login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse('You are not allowed here!!')
    
    if request.method == "POST":
        message.delete()
        return redirect("home")
    return render(request, "home/delete.html", {"obj":message})

@login_required(login_url = 'login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == 'POST':
        # request.FILES is because of the enctype
        form = UserForm(request.POST, request.FILES ,instance=user)
        if form.is_valid():
            form.save()
        return redirect('user-profile', pk = user.id)

    return render(request, 'home/update-user.html', {'form':form})


def topicsPage(request):
    q = request.GET.get("q")  if request.GET.get("q") != None else ""
    topics = Topic.objects.filter(name__icontains = q)
    return render(request, 'home/topics.html', {"topics":topics})


def activityPage(request):
    room_messages = Message.objects.all()
    return render(request, 'home/activity.html', {'room_messages':room_messages})
