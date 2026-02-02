import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser


class BaseCreateModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        
        
class User(AbstractUser):
    phone = models.CharField(max_length=20, unique=True)
    telegram_id = models.BigIntegerField(unique=True)
    district = models.CharField(max_length=150)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    balance = models.IntegerField(default=0)
    about = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='users/', default='users/image.png')
    def __str__(self):
        return self.username
    

class UserActivities(BaseCreateModel):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    amount = models.IntegerField(default=0)
    region = models.CharField(max_length=150)
    video_file_id = models.CharField(max_length=255, null=True, blank=True)
    user = models.ForeignKey(
        User, 
        to_field='phone',  
        on_delete=models.CASCADE, 
        related_name='phone_act',
        db_column='user_phone' 
    )
    
class ActivityLog(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    amount = models.IntegerField(default=0)
    region = models.CharField(max_length=150)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    video_file_id = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.amount} ball"

    
    
