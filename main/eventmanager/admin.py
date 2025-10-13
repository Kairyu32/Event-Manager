from django.contrib import admin
from .models import EventManager, RSVP


@admin.register(EventManager)
class EventManagerAdmin(admin.ModelAdmin):
	list_display = ('id', 'event_name', 'user', 'event_time', 'event_view_count')
	search_fields = ('event_name', 'event_description', 'user__username')
	list_filter = ('event_time',)


@admin.register(RSVP)
class RSVPAdmin(admin.ModelAdmin):
	list_display = ('id', 'event', 'user', 'timestamp')
	search_fields = ('event__event_name', 'user__username')
