from django.contrib import admin
from .models import *
from django.utils.html import format_html

  
admin.site.site_header = "Rony Admin"

   
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('name','mobile','email','city','pic','user_type')

    def display_profile_pic(self, obj):
        return format_html('<img src="{}" width="35" />', obj.profile_pic.url)

    display_profile_pic.short_description = 'Profile Picture'
 
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('company_name','category', 'experience')
    list_display_links = ('experience','company_name')
    # list_editable = ('category',)
    list_filter = ('posted_at',)

@admin.register(Apply_Project)
class Apply_ProjectAdmin(admin.ModelAdmin):
    list_display = ('company_name','title','mobile','city','email','pic','attachments','status')


admin.site.register(Wishlist)
admin.site.register(Subscription)
admin.site.register(Cart)
admin.site.register(Checkout)