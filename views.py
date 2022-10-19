#import from django library

    #import 

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views import View
from django.shortcuts import redirect                   #Used for redirection of webpages
from django.core.paginator import Paginator             #Used for implementing paginated lists
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin

import datetime

from GoClimbApp.models import climbHistory, cragRoute

from .models import *
from .forms import *



import urllib.request
import json


class indexView(View):
    template_name = 'index.html'
    def get(self, request):
        return render(request, self.template_name)

class homeView(LoginRequiredMixin, View):
    login_url='signIn'
    template_name = 'home.html'
    def get(self, request):
        return render(request, self.template_name)
class signInView(View):
    template_name = 'signIn.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home')
        return render(request, self.template_name)

    def post(self, request):
            username = request.POST.get('username')
            password = request.POST.get('password')            
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.info(request, 'Username OR password is incorrect')
            return self.get(request)
        
def logoutUser(request):

        logout(request)
        return redirect('signIn')

class signUpView(View):
    template_name = 'signUp.html'
    form = CreateUserForm()
    context = {'form': form}

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home')
        return render(request, self.template_name, self.context)
    
    def post(self, request):
        self.form = CreateUserForm(request.POST)
        if self.form.is_valid():
            self.form.save()
            username = self.form.cleaned_data.get('username')
            user = User.objects.get(username=username)
            userProfile.objects.create(userID=user)
            messages.success(request, 'Account was created for ' + username)
            return redirect('signIn')
        else:    
            return self.get(request)

class cragsView(LoginRequiredMixin, View):
    login_url='signIn'
    template_name = 'Crags.html'
    def get(self, request):
        return render(request, self.template_name)


#User Dashboard view 
#The level (progress) of user is displayed in the dashboard
class myClimbsView(LoginRequiredMixin, View):
    login_url='signIn'
    template_name = 'MyClimbs.html'

    #an initial score (level) of 0 is assigned to the user 
    prevScore = 0


    def get(self, request):

        #when a user logs a climb from Crag5 page, the level is increased by the grade/difficulty level of the crag
        self.prevScore =  self.prevScore + int(request.GET["p"])
        return render(request, self.template_name,{'score':int(request.GET["p"])+self.prevScore})

class myCommunityView(LoginRequiredMixin, View):
    login_url='signIn'
    template_name = 'MyCommunity.html'

    def get(self, request):
        posts = MBPost.objects.all().order_by('-time')
        posts_paginator = Paginator(posts, 5)
        page_no = request.GET.get('page')
        posts = posts_paginator.get_page(page_no)
        args = {'posts':posts}
        return render(request,self.template_name, args)
    
    def post(self, request):
        message = request.POST.get("message")
        title = request.POST.get("title")
        time = datetime.datetime.now()
        MBPost.objects.create(text=message, title=title, time=time, FKUserProfile=userProfile.objects.get(userID=request.user))
        return self.get(request)

class likePostView(LoginRequiredMixin, View):
    def get(self, request):
        post = MBPost.objects.get(id=request.GET.get("id"))
        try:
            postLikeStatus = MBPostLikeStatus.objects.get(
            FKUserProfile = userProfile.objects.get(userID=request.user), 
            FKMBPost = post)
            postLikeStatus.isLiked = not postLikeStatus.isLiked
            postLikeStatus.save(update_fields=['isLiked'])
        except MBPostLikeStatus.DoesNotExist:
            postLikeStatus = MBPostLikeStatus(
            FKUserProfile = userProfile.objects.get(userID=request.user), 
            FKMBPost = post, isLiked = True)
            postLikeStatus.save()
        finally:
            return redirect('MyCommunity')

class settingsView(LoginRequiredMixin, View):
    login_url='signIn'
    template_name = 'Settings.html'
    def get(self, request):
        return render(request, self.template_name)
    
    
   #####################################################
    # New view of all crags relocate it as you want...
   #####################################################
def Crags(request):
    return render(request,'Crags.html')

class Crags1(LoginRequiredMixin, View):
    login_url='signIn'
    template_name = 'Crags1.html'


    def get(self, request):
        data = {}

        city = 'Wollongong'

        source = urllib.request.urlopen('http://api.openweathermap.org/data/2.5/weather?q=' +
                                            city + '&units=metric&appid=6e1079025f4832f4f4947ebbf8276420').read()
        list_of_data = json.loads(source)



       # if int(list_of_data['rain']['3h']) > 5:
          #  warningData["windWarning"] = "Wind Hazard!"
            
        

        data = {
            "temp": str(list_of_data['main']['temp']) + ' °C',
            "pressure": str(list_of_data['main']['pressure']),
            "humidity": str(list_of_data['main']['humidity']),
            'main': str(list_of_data['weather'][0]['main']),
            'description': str(list_of_data['weather'][0]['description']),
            'icon': list_of_data['weather'][0]['icon'],
            "wind": str(list_of_data['wind']['speed']) + ' m/s'
        }
        print(data)

        
        if float(list_of_data['wind']['speed']) > 4:
            data["windWarning"] = 'Wind Hazard!'

        if str(list_of_data['weather'][0]['main']) == 'Rain':
            data["rainWarning"] = 'Rain Hazard!'
            
        
        print(data)

        return render(request, self.template_name, data)

    def post(self, request):
        
        return self.get(request)



class Crags2(LoginRequiredMixin, View):
    login_url='signIn'
    template_name = 'Crags2.html'
    def get(self, request):
        if(len(request.GET)>0):
            routes = None
            data = request.GET
            print(request.GET)
            rating = int(data['Rating'])
            grade = int(data['Grade'])
            length = data['Rope Length']
            print(rating,grade,length)
            if(length == 'True'):
                routes = cragRoute.objects.filter(rating__gte=rating, grade__gte=grade, length__gte = 25)
            else:
                routes = cragRoute.objects.filter(rating__gte=rating, grade__gte=grade, length__lte = 25)
            return render(request, 'Crags3.html', {'routes':routes, 'length':len(routes)})
        return render(request, self.template_name)
class Crags3(LoginRequiredMixin, View):
    login_url='signIn'
    template_name = 'Crags3.html'
    def get(self, request):
        return render(request, self.template_name)

def Crags4(request):
    return render(request,'Crags4.html')


#Crag5 page 
#Logging crags climbed
class Crags5(LoginRequiredMixin, View):

    login_url='signIn'
    template_name = 'Crags5.html'
  

    
    def get(self, request):

        #access all the cragRoute from database for display 
        self.routes = cragRoute.objects.all()
        context = {"routes":self.routes}
        return render(request, self.template_name, context)

    
    def post(self, request):
 
        #The unique ID of the crag and the crag grade is sent to the MyClimbs page to increase the users level 
        self.cragRoute = request.POST.get('cragRouteID')
        self.cragRouteGrade = request.POST.get('cragRouteGrade')
        return redirect('MyClimbs/?p=%s'%self.cragRouteGrade)

        
       
        
###########################################################
