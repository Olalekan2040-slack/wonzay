from django.db import models
import uuid


class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    source = models.CharField(max_length=50, default="popup", help_text="popup | footer | checkout")
    unsubscribe_token = models.UUIDField(default=uuid.uuid4, unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
