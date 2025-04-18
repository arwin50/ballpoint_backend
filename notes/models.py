from django.db import models
import uuid

class Category(models.Model):
    label = models.CharField(max_length=100, primary_key=True)  # Unique category name
    color = models.CharField(max_length=50)  # Color associated with the category

    def __str__(self):
        return self.label

class NoteDocument(models.Model):
    noteID = models.CharField(primary_key=True, default=uuid.uuid4, max_length=50)
    title = models.CharField(max_length=255)
    categories = models.ManyToManyField(Category)  # Many-to-Many relationship
    notesContent = models.TextField(blank=True)
    date = models.DateField()

    def __str__(self):
        return f"{self.title} ({self.date})"
