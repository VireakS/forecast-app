from django.db import models


# Create your models here.
class ForecastModel(models.Model):
    json = models.JSONField()
    created_at = models.DateTimeField(auto_now=True)
