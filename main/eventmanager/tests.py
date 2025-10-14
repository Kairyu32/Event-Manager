from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import EventManager

# Test cases for the event views and RSVP functionality
class EventsViewTests(TestCase):
	def setUp(self):
		self.client = Client()
		self.user = User.objects.create_user(username='tester', password='pass')

	def test_post_without_event_name_returns_errors(self):
		self.client.login(username='tester', password='pass')
		resp = self.client.post('/', data={
			'event_description': 'desc',
			# missing event_name
			'event_time': '2025-10-13T12:00'
		})
		# Should not be server error
		self.assertNotEqual(resp.status_code, 500)
		self.assertContains(resp, 'Event name is required.')

	def test_created_event_appears_in_list(self):
		# Create an event attached to the user
		EventManager = __import__('eventmanager.models', fromlist=['EventManager']).EventManager
		EventManager.objects.create(
			user=self.user,
			event_name='My Test Event',
			event_description='Description',
			event_time='2025-10-13T12:00'
		)

		resp = self.client.get('/')
		self.assertEqual(resp.status_code, 200)
		self.assertContains(resp, 'My Test Event')

	def test_rsvp_endpoint_behaviour(self):
		# Create event and login
		event = EventManager.objects.create(
			user=self.user,
			event_name='RSVP Event',
			event_description='desc',
			event_time='2025-10-13T12:00'
		)
		self.client.login(username='tester', password='pass')

		# First RSVP - should succeed
		resp1 = self.client.post(f'/event/{event.id}/rsvp/')
		self.assertEqual(resp1.status_code, 200)
		self.assertJSONEqual(resp1.content, {'status': 'success', 'username': self.user.username})

		# Second RSVP - should return exists
		resp2 = self.client.post(f'/event/{event.id}/rsvp/')
		self.assertEqual(resp2.status_code, 200)
		self.assertJSONEqual(resp2.content, {'status': 'exists'})
