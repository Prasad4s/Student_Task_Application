from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout , get_user_model
from django.contrib import messages
from .models import student, LoginUsers, TaskStudent, tasks_zerowaste, User, Profile
from .forms import TaskForm, RegisterForm
from django.contrib.auth.decorators import login_required
import matplotlib.pyplot as plt
import os
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseBadRequest
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.core import serializers
import json
from datetime import datetime
from django.db.models import Count
from django.contrib.auth.hashers import make_password



# Create your views here.

def home(request):
    usernames = tasks_zerowaste.objects.values_list('zerowaste_user__username', flat=True).distinct()
    
    if request.user.is_authenticated:
        profile = request.user.profile
        if profile is not None and profile.role in ['student', 'monitor', 'Teacher']:
            # Redirect to the respective home page for students, monitors, and teachers
            if profile.role == 'student':
                return redirect('student_home')
            elif profile.role == 'monitor':
                return redirect('monitor_home')
            else:
                return render(request, 'home/home.html', {'usernames': usernames})  # Pass usernames to the template
    else:
        return render(request, 'home/home.html', {'usernames': usernames}) 

def tasks_by_username(request, username):
    
    tasks = tasks_zerowaste.objects.filter(zerowaste_user__username=username).values()
    
    
    return JsonResponse(list(tasks), safe=False)


# def get_tasks(request):
#     tasks = TaskStudent.objects.all()
#     task_list = []
#     for task in tasks:
#         task_data = {
#             'id': task.id,
#             'task_name': task.task_name,
#             'task_start_date': task.task_start_date,
#             'task_status': task.task_status,
#             'task_completion_date': task.task_completion_date,
#             'username': task.username.username  # Access the username field of the related student object
#         }
#         task_list.append(task_data)
#     return JsonResponse(json.dumps(task_list), safe=False)


def update_status(request, task_id):
    if request.method == 'POST':
        new_status = request.POST.get('status')
        task = get_object_or_404(tasks_zerowaste, id=task_id)

        # Update the task status
        task.task_status = new_status

        # Save the completion date if it exists in the form data
        completion_date = request.POST.get('completion_date')
        if completion_date:
            task.task_completion_date = completion_date

        # Save the username of the user who is updating the status
        task.updated_by = request.user.username

        # Save the updated task
        task.save()

        messages.success(request, 'Status updated successfully!')

        # Construct the JSON response
        response_data = {
            'status': task.task_status,
        }
        return JsonResponse(response_data)

    return HttpResponseBadRequest('Invalid request method')

    return redirect('home')

def delete_task(request, task_id):
    task = get_object_or_404(tasks_zerowaste, id=task_id)
    task.delete()
    return HttpResponse(status=200)


# @login_required(login_url='home')
User = get_user_model()

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        # Authenticate the user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # User credentials are valid
            login(request, user)

            try:
                profile = user.profile
                if profile is not None and profile.role == 'student':
                    return redirect('student_home')
                elif profile is not None and profile.role == 'monitor':
                    return redirect('monitor_home')
                elif profile is not None and profile.role == 'Teacher':
                    return redirect('home')  # Redirect to 'home' for teachers
            except Profile.DoesNotExist:
                pass

        # User credentials are invalid or no profile found
        messages.error(request, "Invalid username or password")

    return render(request, 'home/login.html')

def user_logout(request):
    logout(request)
    return redirect('user_login')

@login_required
def tasks(request):
    if request.method == 'POST':
        task_name = request.POST.get('task_name')
        task_start_date = request.POST.get('task_start_date')
        username = request.POST.get('username')

        # Check if task_start_date is valid and convert it to a date object
        if task_start_date:
            try:
                task_start_date = datetime.strptime(task_start_date, '%Y-%m-%d').date()
            except ValueError:
                task_start_date = None

        user = User.objects.get(username=username)

        tasks_zerowaste.objects.create(
            task_name=task_name,
            task_start_date=task_start_date,
            zerowaste_user=user,
            username=username,
            task_status='0%',
            task_completion_date=None
        )

        messages.success(request, 'Task Added Successfully')  # Add success message

        # Add any additional logic or redirection after saving the task

    # Filter and retrieve usernames with role "student"
    student_usernames = Profile.objects.filter(role='student').values_list('user__username', flat=True)

    return render(request, 'home/tasks.html', {'usernames': student_usernames})
def get_student_name():
    # Retrieve the student name from the student_data table, assuming you have a specific student in mind
    # Modify this logic based on how you want to retrieve the student name
    student_obj = student.objects.get(id=1)  # Example: Retrieving the student with id=1
    return student_obj.name

def register(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        password = request.POST.get('password')
        role = request.POST['role']  # Retrieve the selected option's value
        
        is_staff = bool(request.POST.get('is_staff'))
        is_active = bool(request.POST.get('is_active'))

        # Check if the username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'home/register.html')
        else:
            # Create a new user object
            new_user = User.objects.create_user(
                username=username,
                password=password,
                first_name=first_name,
                last_name=last_name,
                is_staff=is_staff,
                is_active=is_active
            )
            
            # Save the user object to the database
            new_user.save()
            
            # Create a profile for the user
            profile = Profile.objects.create(user=new_user, role=role)
            
            # Save the profile object to the database
            profile.save()
        
        # Redirect to a success page or any other desired page
        return redirect('user_login')
    
    return render(request, 'home/register.html')

@login_required
def graph(request):
    usernames = tasks_zerowaste.objects.values_list('username', flat=True).distinct()
    selected_username = request.GET.get('username', '')
    return render(request, 'home/graph.html', {'usernames': usernames, 'selected_username': selected_username})

def get_tasks(request, username):
    selected_username = request.GET.get('username')
    tasks = tasks_zerowaste.objects.filter(zerowaste_user__username=username).order_by('id').values('task_name', 'task_status')
    
    return JsonResponse({'tasks': list(tasks)})

@login_required
def graph2(request):
    all_tasks = tasks_zerowaste.objects.all()

    # Prepare the task data for the chart
    task_data = []
    task_names = set()  # Use a set to store unique task names
    for task in all_tasks:
        task_data.append({
            'task_name': task.task_name,
            'task_status': task.task_status,
            'username': task.username
        })
        task_names.add(task.task_name)

    # Pass the task data and task names to the template
    context = {'task_data': task_data, 'task_names': task_names}
    return render(request, 'home/graph2.html', context)



@login_required
def student_home(request):
    # Retrieve the logged-in user
    user = request.user

    # Fetch tasks assigned to the logged-in user
    tasks = tasks_zerowaste.objects.filter(zerowaste_user=user)

    context = {
        'tasks': tasks
    }

    return render(request, 'home/student_home.html', context)

# This update_Stud_Status is for student_home 
def update_stud_status(request, task_id):
    user = request.user
    status = request.POST.get('status')

    task = get_object_or_404(tasks_zerowaste, pk=task_id, zerowaste_user=user)
    task.task_status = status
    task.updated_by = user.username
    task.save()

    return JsonResponse({'message': 'Task status updated successfully.'})

@login_required
def monitor_home(request):
    usernames = tasks_zerowaste.objects.values_list('zerowaste_user__username', flat=True).distinct()
    return render(request, 'home/monitor_home.html', {'usernames': usernames})

# Update_monitor_task is for moniter_home

def update_monitor_task(request, task_id):
    if request.method == 'POST':
        new_status = request.POST.get('status')
        comment = request.POST.get('comment')
        task = get_object_or_404(tasks_zerowaste, id=task_id)

        # Update the task status, comment, and updated_by
        task.task_status = new_status
        task.comment = comment
        task.updated_by = f"{request.user.username} - {request.user.profile.role}"

        # Save the updated task
        task.save()

        # Construct the JSON response
        response_data = {
            'status': task.task_status,
        }
        return JsonResponse(response_data)

    return HttpResponseBadRequest('Invalid request method')