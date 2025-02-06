from django.urls import path
from . import views

app_name = "users"  

urlpatterns = [
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),  
    path('manager/', views.manager_page, name='manager_page'),
    path('employee/', views.employee_page, name='employee_page'),
    path('employee/', views.employee_page, name='employee_page'),
]