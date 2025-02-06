from django.shortcuts import render, redirect
from .models import User

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)

            if user.password == password:  # ❌ Not secure (use hashing in real projects)
                if user.role == 'manager':
                    return redirect('users:manager_page')
                elif user.role == 'employee':
                    return redirect('users:employee_page')
            else:
                return render(request, 'users/login.html', {'error': 'Invalid password'})
        
        except User.DoesNotExist:
            return render(request, 'users/login.html', {'error': 'User not found'})
    
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
            return render(request, 'users/register.html', {'error': 'Passwords do not match'})

        # Check if email is already registered
        if User.objects.filter(email=email).exists():
            return render(request, 'users/register.html', {'error': 'Email already exists'})

        # Save the user
        user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone_number=phone_number,
            birthday=birthday,
            role=role,
            password=password  # ✅ Hash the password before saving
        )
        user.save()

        return render(request, 'users/register.html', {'success': 'Registration successful! You can now login.'})

    return render(request, 'users/register.html')


def manager_page(request):
    return render(request, 'users/manager_page.html')

def employee_page(request):
    return render(request, 'users/employee_page.html')
