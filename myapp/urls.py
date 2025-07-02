from django.contrib import admin
from django.urls import path,include
from myapp import views
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    
    ########################################
    ## Freelancer #
    ########################################
    
    path('',views.index,name="myapp"),
    path("find_project/",views.find_project, name="find_project"),
    path('apply_project/<int:pk>/', views.apply_project, name='apply_project'),
    path('project_applied_applicant/', views.project_applied_applicant, name='project_applied_applicant'),
    path("wishlist/", views.wishlist,name="wishlist"),
    path("add_to_wishlist/<int:pk>/", views.add_to_wishlist,name="add_to_wishlist"),
    path("remove_from_wishlist/<int:pk>/", views.remove_from_wishlist, name="remove_from_wishlist"),
    
    ########################################
    ## common  #
    ########################################
    
    path("registration/",views.registration,name="registration"),
    path("login/",views.login,name="login"),
    path("logout/",views.logout,name="logout"),
    path("change-password/",views.change_password,name="change-password"),
    path("forgot-password/",views.forgot_password,name="forgot-password"),
    path("new-password/",views.new_password,name="new-password"),
    path("otp/",views.otp,name="otp"),
    path("profile/",views.profile,name="profile"),

    ########################################
    ## company  #
    ########################################

    path('index',views.company,name="index"),
    path('post_project/', views.post_project, name='post_project'),
    path('show_all_projects/', views.show_all_projects, name="show_all_projects"),
    path('edit_projects_details/<int:pk>/', views.edit_projects_details, name='edit_projects_details'),
    path('delete_project/<int:pk>/', views.delete_project, name='delete_project'),
    path("applications/",views.applications,name="applications"),
    path('update_application_status/<int:application_id>/<str:status>/', views.update_application_status, name='update_application_status'),
    path('accepted_applications/', views.accepted_applications, name='accepted_applications'),
    path('rejected_applications/', views.rejected_applications, name='rejected_applications'),

    path('download/', views.download_csv, name='download_csv'),
    path('bulkuploadview/',views.bulkuploadview,name="bulkuploadview"),
    path('bulkupload/',views.bulkupload,name="bulkupview"),

    ########################################
    ## Subscription
    ########################################

    path("subscription/",views.subscription,name="subscription"),
    path('cart/', views.cart, name='cart'),
    path('add_to_cart/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<int:pk>/', views.remove_from_cart, name='remove_from_cart'),
    path('increment_quantity/<int:item_id>/', views.increment_quantity, name='increment_quantity'),
    path('decrement_quantity/<int:item_id>/', views.decrement_quantity, name='decrement_quantity'),

    path('checkout/',views.checkout,name='checkout'),
    # path('paymenthandler/', views.paymenthandler, name='paymenthandler'),
    
    # path('failure/', views.failure, name='failure'),  
    # path('success/',views.success,name='success'),

  
    path('payment/',views.pay,name='payment'),
    path('invoice/', views.generate_invoice, name='invoice'),

    # path('create-checkout-session/', views.create_checkout_session, name='create_checkout_session'),  

    # path('checkout/', views.checkout, name='checkout'),  # Update to use order_id
    # path('payment-success/<int:order_id>/', views.paymentSuccessful, name='payment-success'),  # Update to use order_id
    # path('payment-failed/<int:order_id>/', views.paymentFailed, name='payment-failed'),

    ########################################
    ## Admin  #
    ########################################

    path('dashboard',views.admin,name="dashboard"),
    # path('log_admin',views.admin_log_view,name="login_admin"),
    path('adminlog',views.admin_login,name="Adminlog"),
    path('admin_reg',views.admin_reg,name="admin_reg"),
    path('admin_proj',views.admin_project,name="admin_project"),
    path('admin_app_projects',views.admin_applied_project,name='admin_applied'),
    # path('admin_project_create',views.admin_create_view,name='admin_create'),
    path('admin_edit_project/<int:pk>',views.admin_edit_projects_details,name="admin_edit_project"),
    path('admin_del_project/<int:pk>',views.admin_delete_project,name="admin_delete_project"),
    path('admin_users',views.admin_display_user,name="admin_users"),
    path('admin_delete_user/<int:pk>',views.delete_user_admin,name="admin_delete_user"),
    path('admin_update_user/<int:pk>',views.admin_update_user,name="admin_update_user"),
    path('admin_usercsv',views.download_admincsv,name="admin_usercsv"),
    path('admin_app_project',views.total_applied_projects,name="total_applied_projects"),
    path('admin_delete_applied_projects/<int:pk>',views.delete_applied_projects_admin,name="delete_admin_applied_projects"),
    path('admin_project_csv_download',views.download_admin_projects_csv,name="download_admin_projects_csv"),
    path('admin_download_app_projects_csv',views.download_admin_app_projects_csv,name="download_admin_download_app_projects_csv"),
]
