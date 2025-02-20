from django.shortcuts import render, redirect
from .models import Task
from users.models import User 

# Create your views here.

#show all tasks and employees to manager
def manager_tasks(request):
    if not request.session.get('user_role') == 'manager':
        return redirect('users:login')  # Redirect if not a manager

    tasks = Task.objects.all()  # Manager sees all tasks
    employees = User.objects.filter(role='employee')  # List of employees

    return render(request, 'tasks/manager_tasks.html', {'tasks': tasks, 'employees': employees})

#view tasks of each employee based on id get from session
def employee_tasks(request):
    if not request.session.get('user_role') == 'employee':
        return redirect('users:login')  # Redirect if not an employee

    user_id = request.session.get('user_id')  
    tasks = Task.objects.filter(assigned_to_id=user_id)  # Only tasks assigned to logged-in employee

    return render(request, 'tasks/employee_tasks.html', {'tasks': tasks})

#add task for manager
def add_task(request):
    if not request.session.get('user_role') == 'manager':
        return redirect('users:login')  

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        assigned_to_id = request.POST.get('assigned_to')

        assigned_to = User.objects.get(id=assigned_to_id)
        Task.objects.create(title=title, description=description, assigned_to=assigned_to)

        return redirect('tasks:manager_tasks')

    return redirect('tasks:manager_tasks')

#update status by employee
def update_task_status(request, task_id):
    if not request.session.get('user_role') == 'employee':
        return redirect('users:login')  

    task = Task.objects.get(id=task_id)

    if task.assigned_to.id != request.session.get('user_id'):  
        return redirect('tasks:employee_tasks')  

    if request.method == 'POST':
        new_status = request.POST.get('status')
        task.status = new_status
        task.save()

    return redirect('tasks:employee_tasks')

#delate task by manager
def delete_task(request, task_id):
    if not request.session.get('user_role') == 'manager':
        return redirect('users:login')

    task = Task.objects.get(id=task_id)
    task.delete()

    return redirect('tasks:manager_tasks')
