from django.db import models

class Category(models.Model):
    label = models.CharField(max_length=100, unique=True)
    color = models.CharField(max_length=7)

    def __str__(self):
        return self.label
