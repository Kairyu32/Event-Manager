from django.db import models
from django.contrib.auth.models import User
# Create your models here.

# Initialing the EventManager and RSVP models
class EventManager(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    event_name = models.CharField(max_length=100)
    event_description = models.TextField()
    event_image = models.ImageField(upload_to="eventmanager")
    event_view_count = models.PositiveBigIntegerField(default=1)
    event_time = models.DateTimeField()

class RSVP(models.Model):
    event = models.ForeignKey(EventManager, on_delete=models.CASCADE, related_name='rsvps')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('event', 'user')