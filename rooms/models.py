
from django.db import models


class RoomImage(models.Model):
    image = models.ImageField(upload_to='rooms/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    # Store Gemini AI analysis
    analysis = models.TextField(blank=True, default="")

    def __str__(self):
        return f"Room {self.id}"
