from django.contrib import admin

# Register your models here.
from .models import ForecastModel

admin.site.register(ForecastModel)