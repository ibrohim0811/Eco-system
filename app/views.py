from django.shortcuts import render, redirect, get_object_or_404
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
        context = super().get_context_data(**kwargs)
        context['profile_user'] = self.get_object()
        return context
    
    def post(self, request, *args, **kwargs):
   
        self.object = self.get_object() 
        
        image = request.FILES.get('profile_image')
        
        if image:
            
            if self.object.image and self.object.image.name != 'users/image.png':
                self.object.image.delete(save=False)
                
            self.object.image = image
            self.object.save()
            
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
    


# app/views.py
import json
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import render
from django.utils import timezone
import calendar

from .models import UserActivities, ActivityLog
from django.db.models import Count, Sum


@login_required
def _render_dashboard(request, target_user):
    qs = ActivityLog.objects.filter(user=target_user).order_by("-created_at")

    accepted_qs = qs.filter(status="accepted")
    pending_qs = qs.filter(status="pending")
    rejected_qs = qs.filter(status="rejected")

    accepted_count = accepted_qs.count()
    pending_count = pending_qs.count()
    rejected_count = rejected_qs.count()

    total_amount = accepted_qs.aggregate(s=Sum("amount"))["s"] or 0

    status_labels = ["Accepted", "Pending", "Rejected"]
    status_values = [accepted_count, pending_count, rejected_count]

    region_stats = (
        qs.values("region")
        .annotate(total=Count("id"))
        .order_by("-total")[:6]
    )
    region_labels = [r["region"] for r in region_stats]
    region_values = [r["total"] for r in region_stats]

    today = timezone.localdate()
    start = today - timedelta(days=13)

    daily_labels, daily_values = [], []
    for i in range(14):
        d = start + timedelta(days=i)
        daily_labels.append(d.strftime("%d.%m"))
        daily_values.append(accepted_qs.filter(created_at__date=d).count())

    week_labels, week_values = [], []
    start7 = today - timedelta(days=6)
    for i in range(7):
        d = start7 + timedelta(days=i)
        week_labels.append(d.strftime("%a"))
        week_values.append(qs.filter(created_at__date=d).count())

    total_reports = qs.count() or 1
    accept_rate = round((accepted_count / total_reports) * 100)
    pending_rate = round((pending_count / total_reports) * 100)

    radar_labels = ["Tasdiqlanish", "Faollik", "Barqarorlik", "Tezlik", "Tozalik"]
    radar_values = [
        accept_rate,
        min(100, total_reports * 5),
        max(10, 100 - pending_rate),
        min(100, accepted_count * 10),
        min(100, (accepted_count + 1) * 8),
    ]

    activities = qs[:12]

    denom = max(1, total_reports)
    accepted_progress = int((accepted_count / denom) * 100)
    pending_progress = int((pending_count / denom) * 100)
    total_progress = min(100, int((total_reports / 20) * 100))

    weekly_accepted = accepted_qs.filter(created_at__date__gte=today - timedelta(days=6)).count()
    weekly_progress = min(100, int((weekly_accepted / 7) * 100))

    # Calendar
    year = today.year
    month = today.month
    month_name = [
        "Yanvar","Fevral","Mart","Aprel","May","Iyun",
        "Iyul","Avgust","Sentyabr","Oktyabr","Noyabr","Dekabr"
    ][month - 1]

    cal = calendar.monthcalendar(year, month)
    calendar_days = [d for week in cal for d in week]
    while len(calendar_days) < 42:
        calendar_days.append(0)

    context = {
        "target_user": target_user,
        "balance": target_user.balance,
        "total_amount": total_amount,

        "accepted_count": accepted_count,
        "pending_count": pending_count,
        "rejected_count": rejected_count,

        "accepted_progress": accepted_progress,
        "pending_progress": pending_progress,
        "total_progress": total_progress,
        "weekly_progress": weekly_progress,

        "daily_labels": json.dumps(daily_labels),
        "daily_values": json.dumps(daily_values),

        "status_labels": json.dumps(status_labels),
        "status_values": json.dumps(status_values),

        "region_labels": json.dumps(region_labels),
        "region_values": json.dumps(region_values),

        "week_labels": json.dumps(week_labels),
        "week_values": json.dumps(week_values),

        "radar_labels": json.dumps(radar_labels),
        "radar_values": json.dumps(radar_values),

        "calendar_days": calendar_days,
        "today_day": today.day,
        "month_name": month_name,
        "year": year,

        "activities": activities,
    }
    return render(request, "user/act.html", context)


@login_required
def dashboard_me(request):
    return _render_dashboard(request, target_user=request.user)


from django.contrib.auth import get_user_model
from django.http import HttpResponseForbidden

@login_required
def dashboard_user(request, uuid):
    target_user = get_object_or_404(User, uuid=uuid)

    # ✅ faqat admin yoki o‘sha user
    if target_user != request.user and not request.user.is_staff:
        return HttpResponseForbidden("Forbidden")

    return _render_dashboard(request, target_user=target_user) 


def user_out(request):
    logout(request)  
    return redirect('/')