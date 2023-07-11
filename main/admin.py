from django.contrib import admin

# Register your models here.

from .models import *

admin.site.register(Transaction)
admin.site.register(Block)
admin.site.register(LandList)