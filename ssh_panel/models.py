from django.db import models

class CommandHistory(models.Model):
    command = models.CharField(max_length=200)
    timestamp = models.DateTimeField(auto_now_add=True)
    containers = models.TextField()  # Comma-separated container names
    output = models.TextField(blank=True)

    def __str__(self):
        return f"{self.command} @ {self.timestamp}"
