from django.shortcuts import render, redirect, get_object_or_404
from .models import Task
from users.models import User
from django.contrib import messages


#task list for filters
def task_list(request, filter_type=None):
    if filter_type == "completed":
        tasks = Task.objects.filter(status="completed")
    elif filter_type == "delayed":
        tasks = Task.objects.filter(status="delayed")
    elif filter_type == "in_progress":
        tasks = Task.objects.filter(status="in_progress")
    else:
        tasks = Task.objects.all()  # Default: Show all tasks

    if request.session.get('user_role') == 'manager':
        template_name = 'tasks/manager_tasks.html'
    else:
        template_name = 'tasks/employee_tasks.html'

    return render(request, template_name, {"tasks": tasks})



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

#LOGOUT
def log_out(request):
    request.session.flush()  
    return redirect("users:login")  

# this function used in get employees in manger page and thier tasks
def manager_tasks(request):
    # Check if the user is a manager; if not, redirect to the login page
    if request.session.get('user_role') != 'manager':
        return redirect('users:login')  

    # Fetch all tasks from the database
    tasks = Task.objects.all()

    # Fetch all employees (users with the role 'employee')
    employees = User.objects.filter(role='employee')

    # Create a list to store employee data
    employee_data = []

    # Loop through each employee to calculate task statistics
    for employee in employees:
        # Count total tasks assigned to the employee
        total_tasks = Task.objects.filter(assigned_to=employee).count()
        
        # Count delayed tasks assigned to the employee
        delayed_tasks = Task.objects.filter(assigned_to=employee, status='delayed').count()
        
        # Count completed tasks assigned to the employee
        completed_tasks = Task.objects.filter(assigned_to=employee, status='completed').count()

        # Add the employee's data to the list
        employee_data.append({
            'id': employee.id,
            'first_name': employee.first_name,
            'last_name': employee.last_name,
            'total_tasks': total_tasks,
            'delayed_tasks': delayed_tasks,
            'completed_tasks': completed_tasks,
        })

    # Pass the data to the template
    return render(request, 'tasks/manager_tasks.html', {
        'tasks': tasks,
        'employees': employees,
        'employee_data': employee_data,  # Pass employee data to the template
})
