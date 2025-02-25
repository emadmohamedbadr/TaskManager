from django.shortcuts import render, redirect, get_object_or_404
from .models import Task
from users.models import User
from django.contrib import messages


# Show all tasks and employees to the manager
def manager_tasks(request):
    if request.session.get('user_role') != 'manager':
        return redirect('users:login')  

    tasks = Task.objects.all()
    employees = User.objects.filter(role='employee')  

    return render(request, 'tasks/manager_tasks.html', {'tasks': tasks, 'employees': employees})

# View tasks of the logged-in employee
def employee_tasks(request):
    if request.session.get('user_role') != 'employee':
        return redirect('users:login')  

    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('users:login')

    tasks = Task.objects.filter(assigned_to_id=user_id)  

    return render(request, 'tasks/employee_tasks.html', {'tasks': tasks})

# Add a new task (Manager only)
def add_task(request):
    if request.session.get('user_role') != 'manager':
        return redirect('users:login')  

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        assigned_to_id = request.POST.get('assigned_to')
        priority = request.POST.get('priority', 'medium')  # Default to medium if not provided

        if not title or not description or not assigned_to_id:
            messages.error(request, "All fields are required.")
            return redirect('tasks:manager_tasks')

        if priority not in ['low', 'medium', 'high', 'urgent']:
            messages.error(request, "Invalid priority level.")
            return redirect('tasks:manager_tasks')

        assigned_to = get_object_or_404(User, id=assigned_to_id, role='employee')

        Task.objects.create(
            title=title,
            description=description,
            assigned_to=assigned_to,
            priority=priority
        )
        messages.success(request, "Task added successfully.")

    return redirect('tasks:manager_tasks')

#manager update task
def update_task(request, task_id):
    if request.session.get('user_role') != 'manager':
        return redirect('users:login')  

    task = get_object_or_404(Task, id=task_id)

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        priority = request.POST.get('priority')
        status = request.POST.get('status')

        if title:
            task.title = title
        if description:
            task.description = description
        if priority in ['low', 'medium', 'high', 'urgent']:
            task.priority = priority
        if status in ['pending', 'in_progress', 'completed', 'delayed']:
            task.status = status

        task.save()
        messages.success(request, "Task updated successfully.")
        return redirect('tasks:manager_tasks')

    return redirect('tasks:manager_tasks')

# Update task status (Employee only)
def update_task_status(request, task_id):
    if request.session.get('user_role') != 'employee':
        return redirect('users:login')  

    user_id = request.session.get('user_id')
    task = get_object_or_404(Task, id=task_id)

    if task.assigned_to.id != user_id:
        messages.error(request, "You can only update tasks assigned to you.")
        return redirect('tasks:employee_tasks')

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in ['pending', 'in_progress', 'completed', 'delayed']:  
            task.status = new_status
            task.save()
            messages.success(request, "Task status updated successfully.")
        else:
            messages.error(request, "Invalid status update.")

    return redirect('tasks:employee_tasks')

# Delete a task (Manager only)
def delete_task(request, task_id):
    if request.session.get('user_role') != 'manager':
        return redirect('users:login')

    task = get_object_or_404(Task, id=task_id)
    task.delete()
    messages.success(request, "Task deleted successfully.")

    return redirect('tasks:manager_tasks')