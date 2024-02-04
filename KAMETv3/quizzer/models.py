from typing import Any
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class TestUser(models.Model):
    username = models.CharField(max_length=20)
    password = models.CharField(max_length=20)
    email = models.EmailField()
    attempts = models.IntegerField(default=5)
    
    def createUser(self):
        user = User.objects.create_user(username=self.username, password=self.password, email=self.email)
        self.password = ''
        self.user = user
        super().save()

    def delete(self):
        user=User.objects.get(username=self.username)
        user.delete()
        return super().delete()

    def __str__(self):
        return self.username
    
class Paper(models.Model):
    subject = models.CharField(max_length = 20)
    time_allotted = models.IntegerField(default=60)
    number_questions = models.IntegerField(default=10)
    
    def __str__(self):
        return self.subject
    
class Question(models.Model):
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE)
    question_text = models.TextField()

    def __str__(self):
        return self.question_text
    
class UserSolution(models.Model):
    CHECK_CHOICES = [
        ("correct", "Correct"),
        ("incorrect", "Incorrect"),
        ("unchecked", "Unchecked"),
    ]
    test_user = models.ForeignKey(TestUser, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    solution = models.TextField()
    status = models.CharField(max_length=10, choices=CHECK_CHOICES, default="unchecked")

    def __str__(self):
        return self.solution