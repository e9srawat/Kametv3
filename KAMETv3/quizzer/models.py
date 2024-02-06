'''models.py'''
from collections.abc import Iterable
import random
from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class TestUser(models.Model):
    '''TestUser model'''
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="test_user")
    attempts = models.IntegerField(default=1)

    def delete(self, using=None, keep_parents=False):
        '''Deletes the User and the testuser'''
        user = self.user
        user.delete()
        return super().delete(using, keep_parents)

    def attempted(self):
        '''Decrement the attempts counter by 1 whenever user attempts a test'''
        self.attempts -= 1
        self.save()
        
    def solutions(self, paper):
        '''Return solutions submitted by user for a paper'''
        return self.user_solution.filter(question__paper=paper)

    def __str__(self):
        return str(self.user)


class Paper(models.Model):
    '''Paper model'''
    subject = models.CharField(max_length=20)
    time_allotted = models.IntegerField(default=60)
    number_questions = models.IntegerField(default=10)

    def random_question(self, testuser):
        '''get number_questions number of questions for the paper'''
        # pylint: disable=no-member
        user_solved_questions = [i.question.id for i in testuser.user_solution.all()]
        available_questions = self.qpaper.exclude(id__in=user_solved_questions)
        random_questions = random.sample(
            list(available_questions),
            min(self.number_questions, len(available_questions)),
        )
        return random_questions

    def add_question(self, question_text):
        '''Add a question to the paper'''
        # pylint: disable=no-member
        return self.qpaper.create(question_text=question_text)

    def __str__(self):
        return str(self.subject)


class Question(models.Model):
    '''Question model'''
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE, related_name="qpaper")
    question_text = models.TextField()

    def __str__(self):
        return str(self.question_text)


class UserSolution(models.Model):
    '''UserSolution model'''
    CHECK_CHOICES = [
        ("correct", "Correct"),
        ("incorrect", "Incorrect"),
        ("unchecked", "Unchecked"),
    ]
    test_user = models.ForeignKey(
        TestUser, on_delete=models.CASCADE, related_name="user_solution"
    )
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="uquestion"
    )
    solution = models.TextField()
    status = models.CharField(max_length=10, choices=CHECK_CHOICES, default="unchecked")

    def __str__(self):
        return str(self.solution)
