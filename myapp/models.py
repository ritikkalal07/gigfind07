from django.db import models
from django import forms
from django.contrib.auth.hashers import check_password
from django.utils import timezone    

# Create your models here.

    
class Project(models.Model):
    company_name = models.CharField(max_length=100, null=False)
    project_name = models.CharField(max_length=100, null=False)
    title = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    description = models.TextField(max_length=100)
    budget = models.IntegerField(null=False)
    duration = models.CharField(max_length=20)
    posted_at = models.DateTimeField(default=timezone.now)
    skills = models.CharField(max_length=100)
    experience = models.CharField(max_length=100, null=True, blank=True) 
    category = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.company_name} - {self.title}"

                                                                                  
class User(models.Model):
    USER_TYPE_CHOICES = [
        ('company', 'Company'),
        ('applicant', 'Applicant'),
    ]

    name = models.CharField(max_length=255)
    email = models.EmailField()
    mobile = models.CharField(max_length=15)
    address = models.TextField()
    city = models.CharField(max_length=255)
    pincode = models.CharField(max_length=10)
    password = models.CharField(max_length=100)
    pic = models.ImageField(upload_to='pics/')
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    website = models.URLField(blank=True, null=True)
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    def __str__(self):
        return self.name



class Wishlist(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    project=models.ForeignKey(Project,on_delete=models.CASCADE)
   
    def __str__(self):
        return self.user.name+" - "+self.project.company_name
    


class Apply_Project(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    
    company_name = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    mobile = models.CharField(max_length=15)
    address = models.TextField()
    city = models.CharField(max_length=255)
    pincode = models.CharField(max_length=10)
    pic = models.ImageField(upload_to='pics/')
    attachments= models.FileField(upload_to='attachments/', blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')



    def __str__(self):
        return self.name


class Subscription(models.Model):
    subscription_name = models.CharField(max_length=100)
    subscription_month = models.IntegerField(default=0)
    subscription_month_price = models.IntegerField(default=0)
    subscription_month_qty = models.IntegerField(default=0)
    total_price = models.IntegerField(default=0)

    def __str__(self):
        return self.subscription_name


class Cart(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    subscription=models.ForeignKey(Subscription,on_delete=models.CASCADE)    
    razor_pay_order_id = models.CharField(max_length=100,null=True,blank=True)
    razor_pay_payment_id = models.CharField(max_length=100,null=True,blank=True)
    razor_pay_payment_signature = models.CharField(max_length=100,null=True,blank=True)
    def __str__(self):
        return self.user.name
    
class Checkout(models.Model):
    company_name = models.CharField(max_length=255)
    email = models.EmailField()
    mobile = models.CharField(max_length=15)
    address = models.TextField()
    city = models.CharField(max_length=255)
    pincode = models.CharField(max_length=10)
    total_price = models.IntegerField(default=0)
    subscription_name = models.CharField(max_length=100)
    subscription_month = models.IntegerField(default=0)
    subscription_month_price = models.IntegerField(default=0)
    subscription_month_qty = models.IntegerField(default=0)
    payment_type = models.CharField(max_length=25,default='Stripe')

    def __str__(self):
        return self.company_name
    

from django.db import models

class Admin_register(models.Model):
    uname = models.CharField(max_length=50)
    email = models.EmailField()
    password = models.CharField(max_length=128) 

    def __str__(self):
        return self.email

class Admin_login(models.Model):
    #uname = models.CharField(max_length=50)
    email = models.EmailField()
    password = models.CharField(max_length=128)  

    def __str__(self):
        return self.email
