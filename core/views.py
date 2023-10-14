from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User, auth
from django.contrib import messages
from .models import Profile, Post, Like_Post, Followers_Count
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from itertools import chain
import random

# Create your views here.

@login_required(login_url='login')
def index(request):
  user_object = User.objects.get(username=request.user.username)
  user_profile = Profile.objects.get(user=user_object)
  
  user_following_list = []
  feed = []
  
  user_following = Followers_Count.objects.filter(follower=request.user.username)
  
  for users in user_following:
    user_following_list.append(users.user)
  
  for usernames in user_following_list:
    feed_lists = Post.objects.filter(user=usernames)
    feed.append(feed_lists)
    
  feed_list = list(chain(*feed))
  
  #user suggestion starts
  all_users = User.objects.all()
  user_following_all = []
  
  for user in user_following:
    user_list = User.objects.get(username=user.user)
    user_following_all.append(user_list)
    
  new_suggestions_list = [x for x in list(all_users) if (x not in list(user_following_all))]
  current_user = User.objects.filter(username=request.user.username)
  
  final_suggestions_list = [x for x in list(new_suggestions_list) if (x not in list(current_user))]
  random.shuffle(final_suggestions_list)
  
  username_profile = []
  username_profile_list = []
  
  for users in final_suggestions_list:
    username_profile.append(users.id)
    
  for ids in username_profile:
    profile_lists = Profile.objects.filter(id_user=ids)
    username_profile_list.append(profile_lists)
    
  suggestions_username_profile_list = list(chain(*username_profile_list))
    
  
  return render(request, 'index.html', {
    'user_profile': user_profile, 
    'posts': feed_list,
    'suggestions_username_profile_list': suggestions_username_profile_list[:4],
    })

@login_required(login_url='login')
def upload(request):
  
  if request.method == "POST":
    user = request.user.username
    image = request.FILES.get('image_upload')
    caption = request.POST['caption']
    
    new_post = Post.objects.create(user=user, image=image, caption=caption)
    new_post.save()
    
    return redirect('index')
  else:
    return redirect('index')
  
@login_required(login_url='login') 
def search(request):
  
  user_object = User.objects.get(username=request.user.username)
  user_profile = Profile.objects.get(user=user_object)
  
  if request.method == 'POST':
    username = request.POST['username']
    username_object = User.objects.filter(username__icontains=username)
  
    username_profile = []
    username_profile_list = []
    
    for users in username_object:
      username_profile.append(users.id)
      
    for ids in username_profile:
      profile_lists = Profile.objects.filter(id_user=ids)
      username_profile_list.append(profile_lists)
      
    username_profile_list = list(chain(*username_profile_list))
      
  return render(request, 'search.html', {
    'user_profile': user_profile,
    'username_profile_list': username_profile_list,
    })
  

@login_required(login_url='login')
def like_post(request, id):
  username = request.user.username
  post_id = id
  
  post = Post.objects.get(id=post_id)
  
  like_filter = Like_Post.objects.filter(post_id=post_id, username=username).first()
  
  if like_filter is None:
    new_like = Like_Post.objects.create(post_id=post_id, username=username)
    new_like.save()
    post.number_of_likes = post.number_of_likes + 1
    post.save()
    return redirect('index')
  else:
    like_filter.delete()
    post.number_of_likes = post.number_of_likes - 1
    post.save()
    return redirect('index')
  
@login_required(login_url='login')  
def profile(request, pk):
  user_object = User.objects.get(username=pk)
  user_profile = Profile.objects.get(user=user_object)
  user_posts = Post.objects.filter(user=pk)
  user_posts_length = len(user_posts)
  
  follower = request.user.username
  user = pk
  
  user_followers = Followers_Count.objects.filter(user=pk)
  user_following = Followers_Count.objects.filter(follower=pk)
  
  if Followers_Count.objects.filter(follower=follower, user=user).first():
    button_text = "Unfollow"
    
  else:
    button_text = "Follow"
  
  context = {
    'user_object': user_object,
    'user_profile': user_profile,
    'user_posts': user_posts,
    'user_posts_length': user_posts_length,
    'button_text': button_text,
    'follower_count': len(user_followers),
    'following_count': len(user_following)
  }
  return render(request, 'profile.html', context)  
  
@login_required(login_url='login')  
def follow(request):
  if request.method == 'POST':
    follower = request.POST['follower']
    user = request.POST['user']
    
    if Followers_Count.objects.filter(follower=follower, user=user).first():
      delete_follower = Followers_Count.objects.get(follower=follower, user=user)
      delete_follower.delete()
      return redirect('profile', user)
    
    else:
      new_follower = Followers_Count.objects.create(follower=follower, user=user)
      new_follower.save()
      return redirect('profile', user)
    
  else:
    return redirect('/')

@login_required(login_url='login')
def settings(request):
  user_profile = Profile.objects.get(user=request.user)
  
  if request.method == "POST":
    
    if request.FILES.get('image') == None:
      image = user_profile.profile_img
      bio = request.POST['bio']
      location = request.POST['location']
      
      user_profile.profile_img = image
      user_profile.bio = bio
      user_profile.location = location
      user_profile.save()
      
    if request.FILES.get('image') is not None:
      image = request.FILES.get('image')
      bio = request.POST['bio']
      location = request.POST['location']
      
      user_profile.profile_img = image
      user_profile.bio = bio
      user_profile.location = location
      user_profile.save()
      
    return redirect('settings')
  
  return render(request, 'settings.html', {'user_profile': user_profile})

def signup(request):
  
  if request.method == 'POST':
    username = request.POST['username']
    email = request.POST['email']
    password1 = request.POST['password1']
    password2 = request.POST['password2']

    if password1 == password2:
      if User.objects.filter(email=email).exists():
        messages.info(request, "Email taken")
        return redirect('signup')
      elif User.objects.filter(username=username).exists():
        messages.info(request, "Username taken")
        return redirect('signup')
      else:
        user = User.objects.create_user(username=username, email=email, password=password1)
        user.save()
        
        #log user in and redirect to settings page.
        user_login = auth.authenticate(username=username, password=password1)
        auth.login(request, user_login)
        
        #create a profile object for the new user
        user_model = User.objects.get(username=username)
        new_profile = Profile.objects.create(user=user_model, id_user=user_model.id)
        new_profile.save()
        return redirect('settings')
        
    else:
      messages.info(request, "Passwords don't match")
      return redirect('signup')
    
  else:
    return render(request, 'signup.html')
  
def login(request):
  if request.method == 'POST':
    username = request.POST['username']
    password = request.POST['password']
    
    user = auth.authenticate(username=username, password=password)
    
    if user is not None:
      auth.login(request, user)
      return redirect('index')
    
    else:
      messages.info(request, "Credentials invalid.")
      return redirect('login')
    
  else:
    return render(request, 'login.html')

@login_required(login_url='login')  
def logout(request):
  auth.logout(request)  
  return redirect('login')