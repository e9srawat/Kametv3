"""models.py"""

import random
from django.db import models
from django.contrib.auth import get_user_model
from django.core.mail import send_mail


# Create your models here.
class TestUser(models.Model):
    """TestUser model"""
    User=get_user_model()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="test_user")
    attempts = models.IntegerField(default=1)

    def delete(self, using=None, keep_parents=False):
        """Deletes the User and the testuser"""
        self.user.delete()
        return super().delete(using, keep_parents)

    def attempted(self):
        """Decrement the attempts counter by 1 whenever user attempts a test"""
        self.attempts -= 1
        self.save()

    def send_email(self, password):
        '''sends email to user with their credentials'''
        subject = "Welcome to Kamet"
        message = f'''You can login and give the test AT WWW.EXAMPLE.COM \n
        your username is "{self.user.username}" and your password is "{password}"'''
        from_email = "shivansh.rawat@enine.school"
        recipient = [self.user.email]
        send_mail(subject, message, from_email, recipient)

    def __str__(self):
        return str(self.user)


class Paper(models.Model):
    """Paper model"""

    subject = models.CharField(max_length=20)
    time_allotted = models.IntegerField(default=60)
    number_questions = models.IntegerField(default=10)

    def random_question(self, testuser):
        """get number_questions number of questions for the paper"""
        user_solved_questions = [i.question.id for i in testuser.user_solution.all()]
        available_questions = self.qpaper.exclude(id__in=user_solved_questions)
        random_questions = random.sample(
            list(available_questions),
            min(self.number_questions, len(available_questions)),
        )
        return random_questions

    def __str__(self):
        return str(self.subject)


class Question(models.Model):
    """Question model"""

    paper = models.ForeignKey(Paper, on_delete=models.CASCADE, related_name="qpaper")
    question_text = models.TextField()

    def __str__(self):
        return str(self.question_text)


class UserSolution(models.Model):
    """UserSolution model"""

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
