from django.contrib import admin
from .models import *
admin.site.site_header = " Project Management System "
admin.site.site_title = " Project Admin Portal"
admin.site.index_title = "Welcome to Project Management System Admin"
# Register your models here.
admin.site.register(Project)
admin.site.register(AmountReceived)
admin.site.register(AmountReleased)
admin.site.register(PhysicalProgress)
admin.site.register(Expenditure)
admin.site.register(LikelyDate)
admin.site.register(CompletionDate)
admin.site.register(HandoverDate)
admin.site.register(Notification)