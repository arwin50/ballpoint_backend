from django.db import models

class Category(models.Model):
    label = models.CharField(max_length=100, primary_key=True)  # Unique category name
    color = models.CharField(max_length=50)  # Color associated with the category

    def __str__(self):
        return self.label

class NoteDocument(models.Model):
    noteID = models.CharField(max_length=50, primary_key=True)
    title = models.CharField(max_length=255)
    categories = models.ManyToManyField(Category)  # Many-to-Many relationship
    notesContent = models.TextField()
    date = models.DateField()

    def __str__(self):
        return f"{self.title} ({self.date})"
