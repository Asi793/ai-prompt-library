from django.db import models


class Prompt(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    complexity = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'prompts'
        ordering = ['-created_at']

    def __str__(self):
        return self.title
