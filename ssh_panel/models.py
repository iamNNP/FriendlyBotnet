from django.db import models

class Container(models.Model):
    name = models.CharField(max_length=100, unique=True)
    host = models.CharField(max_length=255)
    port = models.IntegerField()
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class CommandHistory(models.Model):
    command = models.CharField(max_length=200)
    timestamp = models.DateTimeField(auto_now_add=True)
    containers = models.TextField()  # Comma-separated container names
    output = models.TextField(blank=True)

    def __str__(self):
        return f"{self.command} @ {self.timestamp}"
