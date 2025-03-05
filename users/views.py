from django.shortcuts import render, redirect
from django.contrib import messages  # For system messages
from .models import User
from django.contrib.auth.hashers import check_password, make_password  # For password hashing


def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)

            # Use Django's check_password for secure password checking
            if check_password(password, user.password):  
                request.session['user_id'] = user.id  
                request.session['user_role'] = user.role  
                request.session['user_name'] = f"{user.first_name} {user.last_name}"  # Store full name in session

                messages.success(request, "Login successful!")  # Success message

                if user.role == 'manager':
                    return redirect('tasks:manager_tasks')
                elif user.role == 'employee':
                    return redirect('tasks:employee_tasks')
            else:
                messages.error(request, 'Invalid password')  
        except User.DoesNotExist:
            messages.error(request, 'User not found')  

        return render(request, 'users/login.html')  # Reload the login page with error messages

    return render(request, 'users/login.html')


def register(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        birthday = request.POST.get('birthday')
        role = request.POST.get('role')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Check if passwords match
        if password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return render(request, 'users/register.html')  # Reload the register page with error message

        # Check if email is already registered
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return render(request, 'users/register.html')  # Reload the register page with error message

        # Hash the password before saving
        hashed_password = make_password(password)

        user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone_number=phone_number,
            birthday=birthday,
            role=role,
            password=hashed_password  # Store hashed password
        )
        user.save()

        messages.success(request, 'Registration successful! You can now login.')
        return redirect('users:login')  # Redirect to login page after successful registration

    return render(request, 'users/register.html')



