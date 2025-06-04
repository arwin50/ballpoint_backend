from django.db import models
from django.conf import settings
import uuid

class Category(models.Model):
    id = models.CharField(
        max_length=255,
        primary_key=True,
        default=uuid.uuid4, 
        editable=False
    )
    label = models.CharField(max_length=255)
    color = models.CharField(max_length=50, blank=True, null=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='categories',
        null=True,  # Allow null for existing records
        blank=True  # Allow blank in forms
    )

    def __str__(self):
        return self.label

class NoteDocument(models.Model):
    noteID = models.CharField(primary_key=True, default=uuid.uuid4, max_length=50)
    title = models.CharField(max_length=255)
    categories = models.ManyToManyField('notes.Category')  # Many-to-Many relationship
    notesContent = models.TextField(blank=True)
    date = models.DateField()
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notes'
    )


    def __str__(self):
        return f"{self.title} ({self.date})"
