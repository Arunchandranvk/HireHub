from django.contrib import admin
from .models import *
# Register your models here.


admin.site.register(Student)
admin.site.register(Department)
admin.site.register(Company)
admin.site.register(JobPosts)
admin.site.register(AppliedStudents)
admin.site.register(TechInterview)