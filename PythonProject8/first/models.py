from django.db import models
from django.contrib.auth.models import User

class Voting(models.Model):
    QUESTION_TYPE_CHOICES = [
        ('single', 'Один вариант'),
        ('multiple', 'Много варинтов'),
    ]
    question = models.CharField(max_length=255)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    voting_type = models.CharField(max_length=10, choices=QUESTION_TYPE_CHOICES, default='single')
    is_anonymous = models.BooleanField(default=False)

    def __str__(self):
        return self.question

class Option(models.Model):
    voting = models.ForeignKey(Voting, related_name='options', on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    votes = models.IntegerField(default=0)


class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    voting = models.ForeignKey(Voting, on_delete=models.CASCADE)
    option = models.ForeignKey(Option, on_delete=models.CASCADE)


class Complaint(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=50, default='Ожидание')
    created_at = models.DateTimeField(auto_now_add=True)


class Comment(models.Model):
    voting = models.ForeignKey(Voting, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class Like(models.Model):
    voting = models.ForeignKey(Voting, related_name='likes', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
