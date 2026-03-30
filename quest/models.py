from django.db import models

class VisitorCount(models.Model):
    total_visitors = models.IntegerField(default=0)