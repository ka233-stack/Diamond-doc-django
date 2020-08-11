from django.shortcuts import render, redirect
from web_models import models
from django.http import HttpResponse

# Create your views here.


def index(request):
    return render(request, 'index.html')

# 登录（成功则跳转至index.html，否则跳转至login.html，并跳出错误提示弹窗）.
def login(request):
    if request.method == 'POST':
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)
        message = "请检查填写内容！"
        if username and password:
            try:
                user = models.Users.objects.get(username=username)
                if user.password == password:
                    request.session['is_login'] = True
                    request.session['username'] = user.username
                    request.session['nickname'] = user.nickname
                    return redirect('/')
                else:
                    message="密码不正确！"
            except:
                message="用户名不存在！"
        return render(request, 'login.html' , {"message" : message } )
    return render(request, 'login.html')

#注册（成功则跳转至index.html，否则跳转至register.html，并跳出错误提示弹窗）.
def register(request):
    if request.method == 'POST':
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)
        repassword = request.POST.get('repassword', None)
        email = request.POST.get('email', None)
        message = "请检查填写内容！"
        if username and password and repassword and email:
            same_name = models.Users.objects.filter(username=username)
            same_email = models.Users.objects.filter(email=email)
            if same_name:
                message="用户名已存在！"
                return render(request, 'register.html' , {"message" : message } )
            if same_email:
                message="邮箱已被注册！"
                return render(request, 'register.html' , {"message" : message } )
            if password != repassword:
                message="两次输入密码不一致！"
                return render(request, 'register.html' , {"message" : message } )
            if len(password) <= 5 or len(password) >= 17:
                message="密码长度不合法(6-16位，区分大小写)！"
                return render(request, 'register.html' , {"message" : message } )
            new_user = models.Users()
            new_user.username = username
            new_user.password = password
            new_user.nickname = username
            new_user.email = email
            new_user.sex = '男'
            new_user.birthday = '2000-01-01'
            new_user.save()
            request.session['is_login'] = True
            request.session['username'] = new_user.username
            request.session['nickname'] = new_user.nickname
            return redirect('/')
        return render(request, 'register.html' , {"message" : message } )
    return render(request, 'register.html')