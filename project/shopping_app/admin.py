from django.contrib import admin
from shopping_app.models import registered_user

class registered_userAdmin(admin.ModelAdmin):
    list_display=('id','Username','Passwd','Userbirthday','Usermail','Usertel')
    list_filter=('id','Username')
    search_fields=('Username',)
    ordering=('id',)
admin.site.register(registered_user,registered_userAdmin)