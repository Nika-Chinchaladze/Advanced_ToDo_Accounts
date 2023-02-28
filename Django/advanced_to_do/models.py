from django.db import models


class Users(models.Model):
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    email = models.CharField(max_length=200, unique=True)
    password = models.CharField(max_length=200)
    user_image = models.ImageField(upload_to="images")

    def __str__(self):
        return self.email


class Lists(models.Model):
    list_name = models.CharField(max_length=200, null=True, blank=True)
    list_type = models.CharField(max_length=100, null=True, blank=True)
    user_id = models.ForeignKey(
        Users, on_delete=models.CASCADE, related_name="lists", null=True, blank=True)


class Tasks(models.Model):
    task_name = models.CharField(max_length=200, null=True, blank=True)
    list_id = models.ForeignKey(
        Lists, on_delete=models.CASCADE, related_name="tasks", null=True, blank=True)
