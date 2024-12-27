from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Course(models.Model):
    subject = models.TextField()
    catalog_number = models.TextField()
    title = models.TextField()
    topic = models.TextField()
    campus = models.TextField()


class Deck(models.Model):
    name = models.TextField()
    writer = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    public = models.BooleanField()

class Card(models.Model):
    writer = models.ForeignKey(User, on_delete=models.CASCADE)
    front = models.TextField()
    back = models.TextField()
    deck = models.ForeignKey(Deck, on_delete=models.CASCADE, related_name='cards')

