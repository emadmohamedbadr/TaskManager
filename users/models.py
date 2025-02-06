from django.db import models

class User(models.Model):
    
    ROLE_CHOICES = [
        ('manager', 'Manager'),
        ('employee', 'Employee'),
    ]

    # Fields
    first_name = models.CharField(max_length=150, blank=False)
    last_name = models.CharField(max_length=150, blank=False)
    email = models.EmailField(unique=True, blank=False)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    birthday = models.DateField(blank=True, null=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='employee')  
    password = models.CharField(max_length=255, blank=False ,null=True)  

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
