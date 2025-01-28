from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,get_user_model
from django.contrib.auth.models  import User
# from django.contrib.auth.decorators  import login_required
from django.contrib import auth,messages

# Create your views here.

def login(request):
    if request.method=="POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        if username and password:
            user = authenticate(username=username ,password=password)
            if user:
                auth.login(request,user)
                messages.success(request,"Login Success")
                return redirect ("/dashboard")
        messages.error(request,"Invalid Credential")
        return render (request,"login.html",{"username":username})
    return render (request,"login.html")

def register(request):
    if request.method=="POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        email = request.POST.get("email")
        try:
            user = User.objects.create_user(username = username , password = password,email = email)
            user.save()
            auth.login(request ,user)

        except:
            messages.error(request,"Username Already exists")
            return render(request,"register.html",{"username":username,"email":email}) 
            
        messages.success(request,"Successfull Created")
        return redirect ("/") 
    return render (request,"register.html")

def logout(request):
    auth.logout(request)
    return redirect("login")

def profile(request):
    return render(request,'profile.html')

def tr(request):
    return render(request,'try.html')
