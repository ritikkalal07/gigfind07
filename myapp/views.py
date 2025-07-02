from datetime import timezone
from django.shortcuts import *
from .models import *
from django.http import HttpResponse
from django.contrib import messages
from django.urls import reverse
from django.shortcuts import render, redirect
# from django.core.mail import EmailMessage
# from django.core.mail import send_mail
from email.message import EmailMessage
import smtplib
import random
import string
import io,csv
from django.contrib.auth.hashers import check_password,make_password


def index(request):
    return render(request, 'Freelancer/index.html')

def hero(request):
    return render(request, 'hero.html')

#################
#     Genral    #
#################

def registration(request):
    if request.method=="POST":
        try:
            User.objects.get(email=request.POST['email'])
            msg="Email Already Registered"
            return render(request,'registration.html',{'msg':msg})
        except:
            if request.POST['password']==request.POST['cpassword']:
                User.objects.create(
                        name=request.POST['name'],
                        email=request.POST['email'],
                        mobile=request.POST['mobile'],
                        website=request.POST['website'],
                        address=request.POST['address'],
                        city=request.POST['city'],
                        pincode=request.POST['pincode'],
                        password=request.POST['password'],
                        pic = request.FILES.get('Pic'), 
                        user_type = request.POST.get('userType'),
                    )
                messages.success(request,"User Sign Up Successfully")
                return render(request,'login.html')
                #msg="User Sign Up Successfully"
                #return render(request,'login.html',{'msg':msg})
            else:
                messages.warning(request,"Password & Confirm Password Does Not Matched !")
                #msg="Password & Confirm Password Does Not Matched"
                return render(request,'registration.html')
    else:
        return render(request,'registration.html')
    


def login(request):
    if request.method == "POST":
        try:
            user = User.objects.get(email=request.POST['email'])
            if user.password == request.POST['password']:
                request.session['email'] = user.email
                request.session['name'] = user.name
                request.session['pic'] = user.pic.url
                wishlist=Wishlist.objects.filter(user=user)
                request.session['wishlist_count']=len(wishlist)
                                
                if user.user_type == "company":
                    return redirect('index')
                else:
                    return redirect('myapp') 
            else:
                messages.warning(request,"Incorrect Password")
                #msg="Incorrect Password"
                return render(request, 'login.html')
        except User.DoesNotExist:
            messages.error(request,"Email Not Registered!")
            #msg="Email Not Registered"
            return render(request, 'registration.html')
    else:
        return render(request, 'login.html')


def logout(request):
	try:
		del request.session['email']
		del request.session['name']
		return render(request,'login.html')
	except:
		return render(request,'login.html')

def get_common_data(request):
	common_data = {}

	if 'email' in request.session:
		user = User.objects.get(email=request.session['email'])
		wishlist=Wishlist.objects.filter(user=user)
		request.session['wishlist_count']=len(wishlist)
	
	return common_data


def change_password(request):
    user = User.objects.get(email=request.session['email'])
    if request.method == "POST":
        # Use .get() to avoid MultiValueDictKeyError
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        cnew_password = request.POST.get('cnew_password')

        if user.password == old_password:
            if new_password == cnew_password:
                user.password = new_password
                user.save()
                return redirect('logout')
            else:
                messages.warning(request,"New password & Confirm New password Do Not Match !")
                return render(request, 'change-password.html')
        else:
            messages.warning(request,"Old Password Does Not Match")
            return render(request, 'change-password.html')
    else:
        context = get_common_data(request)  # type: ignore
        return render(request, "change-password.html", context)



import random
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from .models import User  

def generate_and_send_otp(email, name):
    """Generate a 6-digit OTP and send it to the user's email"""
    otp = random.randint(100000, 999999) 

    subject = 'Your OTP for Password Reset'
    message = f'Hello {name},\n\nYour OTP for password reset is: {otp}\n\nPlease use this OTP to reset your password.'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [email]

    try:
        send_mail(subject, message, from_email, recipient_list)
        return otp  
    except Exception as e:
        return None, str(e)  
    
def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email').strip()  
        
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            messages.error(request, 'User with this email does not exist.')
            return redirect('forgot-password')

        otp = generate_and_send_otp(email, user.name)
        if otp:
            request.session['otp'] = otp
            request.session['email'] = email
            messages.success(request, 'OTP has been sent to your email.')
            return redirect('otp') 
        else:
            messages.error(request, 'Failed to send OTP email. Please try again.')
            return redirect('forgot-password')

    return render(request, 'forgot-password.html')


from django.shortcuts import render, redirect
from django.contrib import messages

def otp(request):
    if request.method == 'GET':
        email = request.session.get('email')  
        if email is None:
            messages.error(request, 'You must request an OTP before verifying it.')
            return redirect('forgot-password')  

        return render(request, 'otp.html', {'email': email})

    email = request.session.get('email')  
    otp = request.session.get('otp') 
    input_otp = request.POST.get('uotp')  

    if otp is None:
        messages.error(request, 'No OTP was generated. Please request an OTP.')
        return redirect('forgot-password')  

    if input_otp and input_otp == str(otp):
        return render(request, 'new-password.html', {'email': email})
    else:
        msg = "Invalid OTP. Please try again."
        return render(request, 'otp.html', {'email': email, 'msg': msg})


def new_password(request):
	email=request.POST['email']
	np=request.POST['new_password']
	cnp=request.POST['cnew_password']

	if np==cnp:
		user=User.objects.get(email=email)
		user.password=np
		user.save()
		return redirect('login')
	else:
		msg="New Password & Confirm New Password Does Not Matched"
		return render(request,'new-password.html',{'email':email,'msg':msg})


from django.contrib import messages

def profile(request):
    if 'email' in request.session:
        user = User.objects.get(email=request.session['email'])
        if request.method == "POST":
            user.name = request.POST.get('name')
            user.email = request.POST.get('email')
            user.mobile = request.POST.get('mobile')
            user.address = request.POST.get('address')
            user.city = request.POST.get('city')
            user.pincode = request.POST.get('pincode')
            user.user_type = request.POST.get('userType')
            if user.user_type == 'company':
                user.website = request.POST.get('website')
                user.company_name = request.POST.get('company_name')
            try:
                user.pic = request.FILES['pic']
            except KeyError:
                pass
            user.save()
            request.session['pic'] = user.pic.url
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile')
        
        if user.user_type == 'company':
            base_template = 'Company/base.html'
        else:
            base_template = 'Freelancer/base.html'
        context = {
            "template_name": base_template,
            "user" : user
        }
        return render(request, 'profile.html', context)
    else:
        return redirect('login')

def profile_view(request):
    user = request.user 
    
    if user.user_type == 'company':
        base_template = 'Company/base.html'
    else:
        base_template = 'Freelancer/base.html'
    
    context = {
        'base_template': base_template,
        'user': user,
    }
    return HttpResponse(context)
    
    return render(request, 'profile.html', context)


 ########################################
    ## company  #
 ########################################

def company(request):
      return render(request, "Company/index.html")

def post_project(request):
    user = None
    context = get_common_data(request)
    if 'email' in request.session:
        user = User.objects.get(email=request.session['email'])
    if request.method == 'POST':
       
        project = Project.objects.create(
            company_name=request.POST['company_name'],
            title=request.POST['title'],
            city=request.POST['city'],
            description=request.POST['description'],
            budget=request.POST['budget'],
            duration=request.POST['duration'],
            posted_at=timezone.now(),
            skills=request.POST['skills'],
            experience=request.POST['experience'],
            category=request.POST['category']
        )

        # msg = "Job Posted Successfully"
        # context.update({"user": user})
        messages.success(request,"Job Posted Successfully!")
        return render(request, 'Company/post_project.html')
    else:
        return render(request, 'Company/post_project.html')

def show_all_projects(request):
    projects = Project.objects.all()  
    user = None
    if 'email' in request.session:
        user = User.objects.get(email=request.session['email'])
        projects=Project.objects.filter(company_name=user)
    return render(request, 'Company/show_all_projects.html', {'projects': projects})



from django.shortcuts import render, redirect, get_object_or_404
from .models import Project 

def edit_projects_details(request, pk):
    project = get_object_or_404(Project, pk=pk)

    if request.method == 'POST':
        # Update project details from form data
        project.company_name = request.POST.get('company_name')
        project.title = request.POST.get('title')
        project.description = request.POST.get('description')
        project.budget = int(request.POST.get('budget'))  
        project.duration = request.POST.get('duration')
        if project.budget <= 0:  
            return render(request, 'Company/edit_projects_details.html', {'project': project, 'error': 'Budget must be positive'})
        project.save()
        return redirect('show_all_projects')  
    return render(request, 'Company/edit_projects_details.html', {'project': project})


def delete_project(request, pk):
    project = get_object_or_404(Project, pk=pk)

    if request.method == 'POST':
        project.delete()
        success_message = f"Project '{project.title}' deleted successfully."
        return redirect('show_all_projects')  

    context = {'project': project}
    return render(request, 'Company/delete_project.html', context)



def applications(request):
    user = None
    if 'email' in request.session:
        user=User.objects.get(email=request.session['email'])
    apply_project = Apply_Project.objects.filter(company_name=user)
    context = get_common_data(request)
    context.update({'apply_project':apply_project})
    return render(request,"Company/applications.html", context)


def update_application_status(request, application_id, status):
    try:
        apply_project = Apply_Project.objects.get(id=application_id)
        apply_project.status = status
        apply_project.save()
    except Apply_Project.DoesNotExist:
        return render(request, 'Company/error.html', {'message': 'Application not found.'})
    
    if status == 'accepted':
        return redirect('accepted_applications')
    else:
        return redirect('rejected_applications')



# def update_application_status(request, application_id, status):
#     try:
#         apply_project = Apply_Project.objects.get(id=application_id)
#         apply_project.status = status
#         apply_project.save()

#         # Email notification only for accepted applications
#         if status == 'accepted':
#             # Get user email from the foreign key relation in Apply_Project
#             user_email = apply_project.user.email  # Assuming a ForeignKey to User model
#             # Create email message
#             message = EmailMessage(
#                 subject='Application for [Project Name] has been Accepted!',
#                 body=f"""
# # Hi {apply_project.user.name},  # Assuming name field in User model

# We are thrilled to inform you that your application for the {apply_project.project_name} project has been accepted!

# This email confirms that your quotation has been approved.

# Please expect further communication regarding the next steps.

# Congratulations!

# Sincerely,

# The [Your Company Name] Team
# """,
#                 from_email='shahau933@gmail.com',
#                 to=[user_email],
#             )

#             # Send email
#             message.send()

#         return redirect('accepted_applications')
#     except Apply_Project.DoesNotExist:
#         return render(request, 'Company/error.html', {'message': 'Application not found.'})
#     except Exception as e:
#         # Handle other exceptions (optional)
#         print(e)
#         return redirect('rejected_applications')



def update_application_status(request, application_id, status):
    try:
        apply_project = Apply_Project.objects.get(id=application_id)
        apply_project.status = status
        apply_project.save()

        if status == 'accepted':
            user_email = apply_project.user.email  # Assuming ForeignKey to User model
            message = EmailMessage(
                subject='Application for [Project Name] has been Accepted!',
                body=f"""
                Hi {apply_project.user.name},  # Assuming name field in User model

                We are thrilled to inform you that your application for the {apply_project.project_name} project has been accepted!

                This email confirms that your quotation has been approved.

                Please expect further communication regarding the next steps.

                Congratulations!

                Sincerely,

                The [Your Company Name] Team
                """,
                from_email='shahau933@gmail.com',  
                to=[user_email],
            )
        else:
             message = EmailMessage(
                subject='Application for [Project Name] has been Rejected!',
                from_email='shahau933@gmail.com',
                to=[user_email],
             )
        # return redirect('accepted_applications')
    # except ObjectDoesNotExist:
    #     return render(request, 'Company/error.html', {'message': 'Application not found.'})
    except Exception as e:
        # Handle other exceptions (optional)
        print(e)
        return redirect('rejected_applications')


def accepted_applications(request):
    apply_project = Apply_Project.objects.filter(status='accepted')
    return render(request, "Company/accepted_applications.html", {'apply_project': apply_project})
    
def rejected_applications(request):
    apply_project = Apply_Project.objects.filter(status='rejected')
    return render(request, "Company/rejected_applications.html", {'apply_project': apply_project})

    

def bulkuploadview(request):
    return render(request,"Company/bulkupload.html")

def bulkupload(request):
    if request.method == 'POST':
        try:
            user = None
            if 'email' in request.session:
                user = User.objects.get(email=request.session['email'])

                data=io.TextIOWrapper(request.FILES['csvfile'].file)
                listData = list(csv.DictReader(data))
                dataObjs = [
                    Project(company_name=i["company_name"],project_name=i["project_name"],title=i["title"],city=i["city"],description=i["description"],budget=i["budget"],duration=i["duration"],posted_at=i["posted_at"],skills=i["skills"],experience=i["experience"],category=i["category"])
                    for i in listData

                ]
                Project.objects.bulk_create(dataObjs)
                messages.success(request,"Job's Posted Successfully!")
                return render(request,"Company/bulkupload.html")
                #return HttpResponse("success")
        except User.DoesNotExist:
            return HttpResponse("User does not exist", status=400)
        except Exception as e:
            return HttpResponse(f"An error occurred: {str(e)}", status=500)
        
        messages.success(request,"Job's Posted Successfully!")
        return render(request,"Company/bulkupload.html")
        #return HttpResponse("Success")

def download_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="user_data.csv"'

    writer = csv.writer(response)

    writer.writerow(['Name', 'Email', 'Mobile', 'Address','City','Pincode','Password','Pic','User_type','Website','Resume'])

    users = User.objects.all().values_list('id', 'name', 'email', 'mobile', 'address','city','pincode','password','pic','user_type','website','resume')

    for user in users:
        writer.writerow(user)

    return response


 ########################################
  ## Subscription
 ########################################
    
def subscription(request):
    subscriptions = Subscription.objects.all()
    return render(request, "Company/subscription.html", {'subscriptions': subscriptions})


from django.http import HttpResponseNotFound
from django.shortcuts import get_object_or_404


def cart(request):
    user = User.objects.get(email=request.session['email'])
    cart_item = Cart.objects.filter(user=user)
    request.session['cart_count']=len(cart_item)

    return render(request, "company/cart.html", {'cart_item': cart_item})

def remove_from_cart(request, pk):
    user = User.objects.get(email=request.session['email'])
    try:
        cart_item = Cart.objects.get(user=user, pk=pk)
        cart_item.delete()

    except Cart.DoesNotExist:
        pass

    return redirect('cart')
    
def add_to_cart(request, pk):
    user = User.objects.get(email=request.session['email'])
    subscription = Subscription.objects.get(pk=pk)

    if not Cart.objects.filter(user=user, subscription=subscription).exists():
        Cart.objects.create(subscription=subscription,
                             user=user
                             )

    return redirect('cart')

def increment_quantity(request, item_id):
    user = User.objects.get(email=request.session['email'])
    cart_item = Cart.objects.get(id=item_id, user=user)
    
    cart_item.subscription.subscription_month_qty += 1
    cart_item.subscription.total_price = cart_item.subscription.subscription_month_qty * cart_item.subscription.subscription_month_price
    cart_item.subscription.save()
    
    return redirect('cart')  

def decrement_quantity(request, item_id):
    user = User.objects.get(email=request.session['email'])
    cart_item = Cart.objects.get(id=item_id, user=user)
    
    if cart_item.subscription.subscription_month_qty > 1:
        cart_item.subscription.subscription_month_qty -= 1
        cart_item.subscription.total_price = cart_item.subscription.subscription_month_qty * cart_item.subscription.subscription_month_price
        cart_item.subscription.save()
    
    return redirect('cart')

from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest
from django.db import transaction
from .models import User, Cart, Checkout, Subscription
import razorpay
import logging


def pay(request):
    return render(request,"Company/payment.html")

def checkout(request):
    user = User.objects.get(email=request.session['email'])
    cart_items = Cart.objects.filter(user=user)
    total_price = sum(item.subscription.total_price for item in cart_items)
    
    if request.method == 'POST':
        Checkout.objects.create(
            company_name=request.POST['company_name'],
            email=request.POST['email'],
            mobile=request.POST['mobile'],
            address=request.POST['address'],
            city=request.POST['city'],
            pincode=request.POST['pincode'],
            subscription_name=request.POST['subscription_name'],
            subscription_month=request.POST['subscription_month'],
            subscription_month_price=request.POST['subscription_month_price'],
            subscription_month_qty=request.POST['subscription_month_qty'],
            total_price=request.POST['total_price']
        )
        return redirect('create_checkout_session')
    
    context = {
        'user': user,
        'cart_items': cart_items,
        'total_price': total_price
    }
    
    return render(request, "company/checkout.html", context)

from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa
import io

def generate_invoice(request):
    user = User.objects.get(email=request.session['email'])
    cart_items = Cart.objects.filter(user=user)
    total_price = sum(item.subscription.total_price for item in cart_items)
    
    context = {
        'user': user,
        'cart_items': cart_items,
        'total_price': total_price,
    }
    
    html = render_to_string('company/invoice.html', context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="invoice.pdf"'
    
    pisa_status = pisa.CreatePDF(io.StringIO(html), dest=response)
    
    if pisa_status.err:
        return HttpResponse("Error generating PDF", status=500)
    
    return response

# def checkout(request):
#     user = User.objects.get(email=request.session['email'])
#     cart_items = Cart.objects.filter(user=user)
#     total_price = sum(item.subscription.total_price for item in cart_items)
#     if request.method == 'POST':
#         Checkout.objects.create(
#             company_name=request.POST['company_name'],
#             email=request.POST['email'],
#             mobile=request.POST['mobile'],
#             address=request.POST['address'],
#             city=request.POST['city'],
#             pincode=request.POST['pincode'],
#             subscription_name=request.POST['subscription_name'],
#             subscription_month=request.POST['subscription_month'],
#             subscription_month_price=request.POST['subscription_month_price'],
#             subscription_month_qty=request.POST['subscription_month_qty'],
#             total_price=request.POST['total_price']
#         )
#         return redirect('create_checkout_session')
#     client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID,settings.RAZORPAY_KEY_SECRECT))

#     payment = client.order.create( {
#             "amount":{total_price},
#             "currency":"INR",
#             "payment_capture":"1"
#         } )
#     Cart.objects.razor_pay_order_id=payment['id']
#     Cart.objects.save()
#         # print(payment)
#     #order_id=payment['id']
#         # print(order_id)
#     context = {
#             #'order_id':order_id,
#             'cart': checkout ,
#             'payment':payment,
#         }
#     return render(request, "company/checkout.html", context,{'user':user, "cart_items": cart_items, "total_price": total_price})








# from django.shortcuts import render, redirect
# from django.contrib import messages
# from django.http import HttpResponseBadRequest
# from django.views.decorators.csrf import csrf_exempt
# from .models import Checkout, Cart
# from django.conf import settings
# import razorpay

# razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

# def checkout(request):
#     user = User.objects.get(email=request.session['email']) 
#     cart_items = Cart.objects.filter(user=user)
    
#     total_price = sum(item.subscription.total_price for item in cart_items)
#     total_price_in_paise = int(total_price * 100) 

#     if request.method == 'POST':
#         Checkout.objects.create(
#             company_name=request.POST['company_name'],
#             email=request.POST['email'],
#             mobile=request.POST['mobile'],
#             address=request.POST['address'],
#             city=request.POST['city'],
#             pincode=request.POST['pincode'],
#             subscription_name=request.POST['subscription_name'],
#             subscription_month=request.POST['subscription_month'],
#             subscription_month_price=request.POST['subscription_month_price'],
#             subscription_month_qty=request.POST['subscription_month_qty'],
#             total_price=total_price  
#         )
#         return redirect('create_checkout_session')

#     payment = razorpay_client.order.create({
#         "amount": total_price_in_paise,  
#         "currency": "INR",
#         "payment_capture": "1"
#     })

#     for cart_item in cart_items:
#         cart_item.razor_pay_order_id = payment['id']
#         cart_item.save()

#     context = {
#         'user': user,
#         'cart_items': cart_items,
#         'total_price': total_price,
#         'total_price_in_paise': total_price_in_paise,
#         'payment': payment,
#         'razorpay_order_id': payment['id'],
#         'razorpay_merchant_key': settings.RAZORPAY_KEY_ID,
#         'currency': 'INR',
#         'callback_url': 'paymenthandler/',
#     }
#     return render(request, "company/checkout.html", context)

# @csrf_exempt
# def paymenthandler(request):
#     if request.method == "POST":
#         try:
#             payment_id = request.POST.get('razorpay_payment_id', '')
#             razorpay_order_id = request.POST.get('razorpay_order_id', '')
#             signature = request.POST.get('razorpay_signature', '')
            
#             params_dict = {
#                 'razorpay_order_id': razorpay_order_id,
#                 'razorpay_payment_id': payment_id,
#                 'razorpay_signature': signature
#             }

#             result = razorpay_client.utility.verify_payment_signature(params_dict)

#             if result is None:  
#                 try:
#                     cart_items = Cart.objects.filter(razor_pay_order_id=razorpay_order_id)
#                     if cart_items.exists():
#                         total_price = sum(item.subscription.total_price for item in cart_items)
#                         amount_in_paise = int(total_price * 100)
#                         razorpay_client.payment.capture(payment_id, amount_in_paise)

#                         return redirect('success', order_id=razorpay_order_id)
#                 except Exception as e:
#                     print(f"Error capturing payment: {e}")
#                     return redirect('failure', order_id=razorpay_order_id)
#             else:
#                 return redirect('failure', order_id=razorpay_order_id)

#         except Exception as e:
#             print(f"Error processing payment: {e}")
#             return HttpResponseBadRequest("Invalid payment data")

#     return HttpResponseBadRequest("Invalid request method")


# import uuid
# from django.conf import settings
# from django.urls import reverse
# from .models import Subscription  # Ensure you import the Order model
# from paypal.standard.forms import PayPalPaymentsForm

# def checkout(request):
#     user = User.objects.get(email=request.session['email'])
#     cart_items = Cart.objects.filter(user=user)
#     total_price = sum(item.subscription.total_price for item in cart_items)

#     if request.method == 'POST':
#         order = Subscription.objects.create(
#             company_name=request.POST['company_name'],
#             email=request.POST['email'],
#             mobile=request.POST['mobile'],
#             address=request.POST['address'],
#             city=request.POST['city'],
#             pincode=request.POST['pincode'],
#             subscription_name=request.POST['subscription_name'],
#             subscription_month=request.POST['subscription_month'],
#             subscription_month_price=request.POST['subscription_month_price'],
#             subscription_month_qty=request.POST['subscription_month_qty'],
#             total_price=total_price  # Use the calculated total price
#         )

#         host = request.get_host()
#         paypal_checkout = {
#             'business': settings.PAYPAL_RECEIVER_EMAIL,
#             'amount': total_price,  # Set the total price
#             'item_name': order.subscription_name,
#             'invoice': uuid.uuid4(),  # Unique invoice number
#             'currency_code': 'USD',  # Change to your currency
#             'notify_url': f"http://{host}{reverse('paypal-ipn')}",
#             'return_url': f"http://{host}{reverse('payment-success', kwargs={'order_id': order.id})}",
#             'cancel_url': f"http://{host}{reverse('payment-failed', kwargs={'order_id': order.id})}",
#         }

#         paypal_payment = PayPalPaymentsForm(initial=paypal_checkout)

#         context = {
#             'user': user,
#             'cart_items': cart_items,
#             'total_price': total_price,
#             'paypal': paypal_payment,
#         }

#         return render(request, 'company/checkout.html', context)

#     context = {
#         'user': user,
#         'cart_items': cart_items,
#         'total_price': total_price,
#     }

#     return render(request, "company/checkout.html", context)



# @csrf_exempt
# def paymenthandler(request):
#      if request.method == "POST":
#         try:
#             payment_id = request.POST.get('razorpay_payment_id', '')
#             order_id = request.POST.get('razorpay_order_id','')
#             signature = request.POST.get('razorpay_signature','')
#             params_dict = { 
#             'razorpay_order_id': order_id, 
#             'razorpay_payment_id': payment_id,
#             'razorpay_signature': signature
#             }
#             try:
#                 cart_items = Cart.objects.get(razorpay_order_id=order_id)
#             except:
#                 return HttpResponse("505 Not Found")
#             cart_items.razorpay_payment_id = payment_id
#             cart_items.razorpay_signature = signature
#             cart_items.save()
#             result = razorpay_client.utility.verify_payment_signature(params_dict)
#             if result==None:
#                 total_price = sum(item.subscription.total_price for item in cart_items)
#                 amount_in_paise = int(total_price * 100)
#                #  amount = cart_items.total_amount * 100   #we have to pass in paisa
#                 try:
#                     razorpay_client.payment.capture(payment_id, amount_in_paise)
#                     cart_items.payment_status = 1
#                     cart_items.save()
                    
#                     return render(request, 'company/paymentsuccess.html',{'id':cart_items.id})
#                 except:
#                     cart_items.payment_status = 2
#                     cart_items.save()
#                     return render(request, 'company/paymentfailed.html')
#             else:
#                 cart_items.payment_status = 2
#                 cart_items.save()
#                 return render(request, 'company/paymentfailed.html')
#         except:
#             return HttpResponse("505 not found")

# def failure(request):
#     order_id = request.GET.get('order_id')  
#     messages.warning(request, 'Payment Failed!') 
#     return redirect('company/checkout.html')  

# def success(request):
#     order_id = request.GET.get('order_id') 
#     try:
#         cart = Checkout.objects.get(razor_pay_order_id=order_id)
#         cart.is_paid = True
#         cart.save()
        
#         messages.success(request, 'Payment Successful!')  
#     except Checkout.DoesNotExist:
#         messages.error(request, 'Checkout not found.')  

#     return redirect('company/checkout.html')


# from django.shortcuts import render, get_object_or_404
# from .models import Subscription  # Ensure you import your Order model

# def paymentSuccessful(request, order_id):
#     # Retrieve the order using the provided order_id
#     order = get_object_or_404(Subscription, id=order_id)

#     # Render the payment success template with order details
#     messages.success(request, 'Payment Success.',{'order': order})

#     # return render(request, 'payment-success.html', {'order': order})

# def paymentFailed(request, order_id):
#     # Retrieve the order using the provided order_id
#     order = get_object_or_404(Subscription, id=order_id)

#     # Render the payment failed template with order details
#     messages.error(request, 'Payment Failed.', {'order': order})
#     # return render(request, 'payment-failed.html', {'order': order})


#################
#   Freelancer  #
#################

def find_project(request):
    projects = Project.objects.all()
    search_query = request.GET.get('search_query')
    
    if search_query:
        projects = Project.objects.filter(category__icontains=search_query)

    context = get_common_data(request)
    context.update( {'projects': projects})
    return render(request,"Freelancer/find_project.html",context)


def apply_project(request, pk):
    if 'email' in request.session:
        user = User.objects.get(email=request.session['email'])
        projects = Project.objects.get(pk=pk)

        if request.method == 'POST':
            Apply_Project.objects.create(
                company_name=request.POST['company_name'],
                title=request.POST['title'],
                name=request.POST['name'],
                email=request.POST['email'],
                mobile=request.POST['mobile'],
                address=request.POST['address'],
                city=request.POST['city'],
                pincode=request.POST['pincode'],
                attachments=request.FILES.get('attachments'),
            )
            messages.success(request,"Job Applied Successfully!")
            return render(request, 'Freelancer/apply_project.html')
        else:
            context = get_common_data(request)
            context.update({'user': user, 'projects': projects, 'pk': pk})
            # context = {'projects': projects, 'user': user , 'pk' : pk}
            return render(request, 'Freelancer/apply_project.html', context)
    else:
        return redirect('login')  


def project_applied_applicant(request):
    user = None
    apply_project = None  
    if 'email' in request.session:
        apply_project = Apply_Project.objects.filter(email=request.session['email'])
            
    context = get_common_data(request)
    context.update({'apply_project': apply_project})
    return render(request, "Freelancer/project_applied_applicant.html", context)



def wishlist(request):
    user = None
    if 'email' in request.session:
        user = User.objects.get(email=request.session['email'])
    wishlist_items = Wishlist.objects.filter(user=user)
    context = get_common_data(request)
    context.update({'wishlist':wishlist_items})
    return render(request, 'Freelancer/wishlist.html',context)


from django.shortcuts import get_object_or_404

def add_to_wishlist(request, pk):
    user = User.objects.get(email=request.session['email'])
    projects = get_object_or_404(Project, pk=pk)
    
    if 'email' in request.session:
        if not Wishlist.objects.filter(user=user, project=projects).exists():
            Wishlist.objects.create(project=projects, user=user)

            wishlist_count = Wishlist.objects.filter(user=user).count()
            request.session['wishlist_count'] = wishlist_count
    else:
        messages.error(request, 'Email not found in session.')
        return redirect('login')  

    return redirect("wishlist")


def remove_from_wishlist(request, pk):
    user = User.objects.get(email=request.session['email'])
    try:
        wishlist_item = Wishlist.objects.get(user=user, pk=pk)
        wishlist_item.delete()
    except Wishlist.DoesNotExist:
        pass  
    
    return redirect("wishlist")



########################################
## Admin  #
########################################

def admin_project(request):
      projects = Project.objects.all()
    #   count=Project.objects.count()

    #   request.session['count']=count
      return render(request, "Admin/admin_projects.html", {'projects': projects})
def admin_applied_project(request):
      projects = Apply_Project.objects.all()
    #   count=Project.objects.count()

    #   request.session['count']=count
      return render(request, "Admin/admin_applied_projects.html", {'projects': projects})

def admin_create_view(request):
     return render(request,'Admin/admin_create_projects.html')
# def post_project(request):
#     user = None
#     context = get_common_data(request)
#     if 'email' in request.session:
#         user = User.objects.get(email=request.session['email'])
#     if request.method == 'POST':
       
#         project = Project.objects.create(
#             company_name=request.POST['company_name'],
#             title=request.POST['title'],
#             city=request.POST['city'],
#             description=request.POST['description'],
#             budget=request.POST['budget'],
#             duration=request.POST['duration'],
#             posted_at=timezone.now(),
#             skills=request.POST['skills'],
#             experience=request.POST['experience'],
#             category=request.POST['category']
#         )
        
#         msg = "Job Posted Successfully"
#         context.update({"user": user})
#         return render(request, 'Admin/admin_create_projects.html', {'msg': msg, 'context': context})
#     else:
#         return render(request, 'Admin/admin_create_projects.html', {'user': user, 'context': context})

def admin_edit_projects_details(request, pk):
    project = get_object_or_404(Project, pk=pk)

    if request.method == 'POST':
        # Update project details from form data
        project.company_name = request.POST.get('company_name')
        project.title = request.POST.get('title')
        project.description = request.POST.get('description')
        project.budget = int(request.POST.get('budget'))  
        project.duration = request.POST.get('duration')
        if project.budget <= 0:  
            return render(request, 'Admin/admin_edit_project.html', {'project': project, 'error': 'Budget must be positive'})
        project.save()
        return redirect('admin_project')  
    return render(request, 'Admin/admin_edit_project.html', {'project': project})


def admin_delete_project(request, pk):
    project = get_object_or_404(Project, pk=pk)

    if request.method == 'GET':
        project.delete()
        success_message = f"Project '{project.title}' deleted successfully."
        return render(request, 'Admin/admin_projects.html') 

    context = {'project': project}
    return render(request, 'Admin/admin_projects.html', context)
def admin_display_user(request):
     users=User.objects.all()
     return render(request, 'Admin/display_user.html', {"users": users})

def admin_delete_user(request, pk):
    user = get_object_or_404(User, pk=pk)

    if request.method == 'GET':
        user.delete()
        success_message = f"User deleted successfully."
        return render(request, 'Admin/admin_projects.html') 

    context = {'user': user}
    return render(request, 'Admin/admin_projects.html', context)
def delete_user_admin(request, pk):
     user=get_object_or_404(User, pk=pk)
     if request.method == 'GET':
          user.delete()
          return render(request, 'Admin/display_user.html')
def admin_update_user(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
         user.name=request.POST.get('new_name')
         user.email=request.POST.get('new_email')
         user.mobile=request.POST.get('new_mobile')
         user.address=request.POST.get('new_address')
         user.city=request.POST.get('new_city')
         user.pincode=request.POST.get('new_pincode')
         user.password=request.POST.get('new_password')
         user.picture=request.POST.get('new_picture')
         #user.user_type=request.POST.get('user_type')
         #user.website=request.POST.get('website')
         #user.resume=request.POST.get('resume')
         user.save()
         return redirect('admin_users')
    return render(request, 'Admin/admin_edit_users.html', {'user': user})

def download_admincsv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="user_data_for_admin.csv"'

    writer = csv.writer(response)

    writer.writerow(['Name', 'Email', 'Mobile', 'Address','City','Pincode','Password','Pic','User_type','Website','Resume'])

    users = User.objects.all().values_list('id', 'name', 'email', 'mobile', 'address','city','pincode','password','pic','user_type','website','resume')

    for user in users:
        writer.writerow(user)

    return response
def total_applied_projects(request):
     ap=Apply_Project.objects.all().count()
     return render(request,'Admin/dashboard.html',{'ap':ap})

def delete_applied_projects_admin(request,pk):
     ap=get_object_or_404(Apply_Project, pk=pk)
     if request.method == 'GET':
          ap.delete()
          return render(request,'Admin/admin_applied_projects.html',{'ap':ap})
     
def download_admin_user_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="user_data_for_admin.csv"'

    writer = csv.writer(response)

    writer.writerow(['Name', 'Email', 'Mobile', 'Address','City','Pincode','Password','Pic','User_type','Website','Resume'])

    users = User.objects.all().values_list('id', 'name', 'email', 'mobile', 'address','city','pincode','password','pic','user_type','website','resume')

    for user in users:
        writer.writerow(user)

    return response
def download_admin_projects_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="user_data_for_project_admin.csv"'

    writer = csv.writer(response)

    writer.writerow(['id', 'Project name', 'title', 'City','Description','Budget','Duration','Posted at','Skills','Experience','Category','Company Name'])

    projects = Project.objects.all().values_list('id', 'project_name', 'title', 'city','description','budget','duration','posted_at','skills','experience','category','company_name')

    for project in projects:
        writer.writerow(project)

    return response
def download_admin_app_projects_csv(request):
     response = HttpResponse(content_type='text/csv')
     response['Content-Disposition'] = 'attachment; filename="user_data_for_apply_project_admin.csv"'

     writer = csv.writer(response)

     writer.writerow(['ID','COMPANY_NAME','TITLE','NAME','EMAIL','MOBILE','ADDRESS','CITY','PINCODE','PIC','ATTACHMENTS','STATUS'])

     apply_projects = Apply_Project.objects.all().values_list('id','company_name','title','name','email','mobile','address','city','pincode','pic','attachments','status')

     for apply_project in apply_projects:
            writer.writerow(apply_project)

     return response



from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import AdminRegisterForm, AdminLoginForm  # Import the forms from forms.py

def admin_reg(request):
    if request.method == 'POST':
        form = AdminRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration successful. Please log in.')
            return redirect('Adminlog')
    else:
        form = AdminRegisterForm()
    return render(request, 'Admin/admin_register.html', {'form': form})

def admin(request):
    return render(request, "Admin/dashboard.html")
    
def admin_login(request):
    projects = Project.objects.all().count()
    users=User.objects.all().count()
    if request.method == 'POST':
        form = AdminLoginForm(request.POST)
        if form.is_valid():
            # Successful login logic (e.g., set session)
            messages.success(request, 'Login successful.')
            #return redirect('Admin/dashboard.html')  # Redirect to some dashboard or home page
            return render(request, "Admin/dashboard.html",{'projects':projects,'users':users})
        else:
            return render(request, 'Admin/Admin_login.html', {'error': 'Invalid credentials'})
    else:
        form = AdminLoginForm()
    return render(request, 'Admin/Admin_login.html', {'form': form})

