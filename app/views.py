from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin

from django.views.generic import (
    TemplateView, CreateView, ListView,
    UpdateView, DeleteView, DetailView, 
    FormView
)

from django.contrib.auth import login, logout

from .forms import UserLoginForm
from .models import User, UserActivities
from .mixins import NotLoginRequiredMixin


class AnimationTemplateView(TemplateView):
    template_name = "animate.html"


class MainTemplateView(TemplateView):
    template_name = "index.html"
    

class UserInfoDetailView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'user/user_info.html'    
    login_url = "auth/login.html"
    
    slug_field = 'uuid' 
    slug_url_kwarg = 'uuid'
    
    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        user = self.request.user
        data['user'] = user
        return data
    
    def post(self, request, *args, **kwargs):
        profile = request.user  
        image = request.FILES.get('profile_image')
        if image:
            profile.image = image
            profile.save()
        return redirect('main')
    
    
    
class UserLoginView(NotLoginRequiredMixin, FormView):
    form_class = UserLoginForm
    template_name = 'auth/login.html'
    success_url = '/'
    
    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = User.objects.filter(username=username).first()
        if user and user.check_password(password):
            login(self.request, user)
            return redirect('/')
        return super().form_valid(form)
    


class ActivityListView(LoginRequiredMixin, ListView):
    model = UserActivities
    template_name = "user/act.html"
    context_object_name = "activities"

    def get_queryset(self):
        qs = UserActivities.objects.filter(user=self.request.user)
        print("ACTIVITIES:", qs.count())
        return qs.order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["sent_count"] = UserActivities.objects.filter(
            user=self.request.user
        ).count()

        return context


def user_out(request):
    logout(request)  
    return redirect('/')