from django.db import models
from django.contrib.auth.models import User
import os


class ChatMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='chat_messages')
    session_key = models.CharField(max_length=64, blank=True, null=True, db_index=True)
    message = models.TextField()
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        user_label = self.user.username if self.user else f"Session {self.session_key[:8] if self.session_key else 'anon'}"
        return f"{user_label} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"


class TravelDocument(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='travel_documents')
    session_key = models.CharField(max_length=64, blank=True, null=True, db_index=True)
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='travel_documents/', null=True, blank=True)
    file_data = models.BinaryField(null=True, blank=True, help_text="In-database binary storage for serverless Vercel and free PDF viewing")
    mime_type = models.CharField(max_length=100, default='application/pdf')
    file_size = models.IntegerField(default=0, help_text="File size in bytes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    @property
    def formatted_size(self):
        if self.file_size < 1024:
            return f"{self.file_size} B"
        elif self.file_size < 1024 * 1024:
            return f"{self.file_size / 1024:.1f} KB"
        else:
            return f"{self.file_size / (1024 * 1024):.1f} MB"

    @property
    def extension(self):
        _, ext = os.path.splitext(self.name)
        return ext.lower()
