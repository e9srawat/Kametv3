from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.TestUser)
admin.site.register(models.Paper)
admin.site.register(models.Question)
admin.site.register(models.UserSolution)