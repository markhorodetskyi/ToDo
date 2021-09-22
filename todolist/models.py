from django.db import models
from django.contrib.auth.models import User


class Todo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=20)
    description = models.TextField(max_length=1000)
    priority_choices = (("LOW", "low"),
                        ("AVERAGE", "average"),
                        ("HIGH", "high"))
    priority = models.CharField(max_length=9, choices=priority_choices, default="LOW")
    complete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateField()

    def __str__(self):
        return self.title
