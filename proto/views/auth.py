from django.core.urlresolvers import reverse
from django.views.generic import View
from django.contrib.auth import authenticate, login, logout
from proto.forms import PhotographerForm, UserForm
from django.shortcuts import render, redirect
from .common import LoginRestrictedView


class Login(View):
    TEMPLATE_NAME = 'login.html'

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']
        u = authenticate(username=username, password=password)
        if u and u.is_active:
            login(request, u)
            redirect_url = request.GET.get('next') or '/'
            return redirect(redirect_url)
        else:
            msg = 'Invalid credentials or inactive account'
        context = {'msg': msg}
        return render(request, self.TEMPLATE_NAME, context)

    def get(self, request):
        return render(request, self.TEMPLATE_NAME)


class Lougout(LoginRestrictedView):
    def get(self, request):
        logout(request)
        return redirect('/')


class Register(View):
    TEMPLATE_NAME = 'register.html'

    def post(self, request):
        registered = False
        user_form = UserForm(request.POST or None)
        photographer_form = PhotographerForm(request.POST or None)
        if user_form.is_valid() and photographer_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            photographer_form.instance.user = user
            photographer_form.save()
            registered = True
        context = {
            'user_form': user_form,
            'photographer_form': photographer_form,
            'js_handler': 'personal_details'
        }
        if registered:
            return redirect(reverse('login'))
        return render(request, self.TEMPLATE_NAME, context)

    def get(self, request):
        context = {
            'user_form': UserForm(),
            'photographer_form': PhotographerForm(),
            'js_handler': 'personal_details'
        }
        return render(request, self.TEMPLATE_NAME, context)
