from django.db import models
from django.contrib.auth.hashers import check_password as django_check_password
from django.utils import timezone
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.contrib.auth import get_user_model


# Create your models here.
class student(models.Model):
    name = models.CharField(max_length=100)
    username = models.CharField(max_length=100, primary_key=True)
    password = models.CharField(max_length=100)

    class Meta:
        managed=True
        db_table = 'student'

class TaskStudent(models.Model):
    username = models.ForeignKey(student, on_delete=models.CASCADE, db_column='username')
    task_name = models.CharField(max_length=100)
    task_status = models.CharField(max_length=100)
    task_start_date = models.DateField()
    task_completion_date = models.DateField(null=True)

    class Meta:
        db_table = 'tasks'
        # When i select the username and add task that data should be stored in 

class LoginUsers(models.Model):
    name = models.CharField(max_length=100)
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField()
    password = models.CharField(max_length=100)

    class Meta:
        db_table = 'login_users'

class User(AbstractUser):
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    password = models.CharField(max_length=128)
    username = models.CharField(unique=True, max_length=150)
    role = models.CharField(max_length=100)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    is_superuser = models.BooleanField(default=False)
    date_joined=timezone.now()
    groups = models.ManyToManyField(Group, related_name='home_users', blank=True, db_table='home_user_groups')
    user_permissions = models.ManyToManyField(Permission, related_name='home_users', blank=True, db_table='home_user_user_permissions')
    

    class Meta:
        managed = False
        db_table = 'auth_user'

User = get_user_model()

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=100)

class tasks_zerowaste(models.Model):
    zerowaste_user = models.ForeignKey(User, on_delete=models.CASCADE)
    task_name = models.CharField(max_length=100)
    task_status = models.CharField(max_length=20)
    task_start_date = models.DateField()
    task_completion_date = models.DateField()
    username = models.CharField(max_length=50)
    updated_by = models.CharField(max_length=100, default='')
    comment = models.CharField(max_length=100)

    class Meta:
        db_table = 'tasks_zerowaste'


