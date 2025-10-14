from django.shortcuts import render, redirect
from .models import EventManager, RSVP
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required
from datetime import datetime

# Create your views here.

# Logic for user registration
def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid(): # Checks username isn't taken, password meets criteria, etc.
            user = form.save()
            login(request, user)
            return redirect('/') # Redirect to homepage after successful registration
    else:
        form = UserCreationForm()
    return render(request, 'event/register.html', {'form': form}) # Sends the user back to registration page if GET or form invalid

# Logic for user login
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid(): # Checks username and password are correct
            user = form.get_user()
            login(request, user) # Logs the user in
            print("User logged in")
            return redirect('/') # Redirect to homepage after successful login
        else:
            print("Form invalid:", form.errors) # Debugging line to see why login failed
            return render(request, 'event/login.html', {'form': form})
    else:
        form = AuthenticationForm() # Empty form for GET request
    return render(request, 'event/login.html', {'form': form})

# Simple logout logic   
def logout_view(request):
    logout(request)
    return redirect('/')

def events(request):
    if request.method == 'POST':
        # Only authenticated users may create events (template only shows the form to logged-in users,
        # but a POST can still be made directly). Validate required fields before creating the DB record
        if not request.user.is_authenticated:
            return HttpResponseForbidden("You must be logged in to add events.")

        data = request.POST
        event_image = request.FILES.get('event_image')
        event_name = (data.get('event_name') or '').strip()
        event_description = (data.get('event_description') or '').strip()
        event_time_str = data.get('event_time')

        # Basic validation: event_name and event_time are required by the UI/UX
        errors = []
        if not event_name:
            errors.append('Event name is required.')
        if not event_description:
            errors.append('Event description is required.')

        event_time = None
        if event_time_str:
            try:
                event_time = datetime.strptime(event_time_str, '%Y-%m-%dT%H:%M')
            except ValueError:
                errors.append('Invalid date/time format for event_time.')
        else:
            errors.append('Event date/time is required.')

        if errors:
            # Re-render the events page with errors and current queryset
            queryset = EventManager.objects.all()
            context = {'events': queryset, 'errors': errors}
            return render(request, 'event/events.html', context)

        # Create the event (attach the current user)
        EventManager.objects.create(
            user=request.user,
            event_image=event_image,
            event_name=event_name,
            event_description=event_description,
            event_time=event_time
        )
        return redirect('/')

    queryset = EventManager.objects.all()

    if request.GET.get('search'):
        queryset = queryset.filter(
            event_name__icontains=request.GET.get('search')
        )
    
    context = {'events': queryset}
    return render(request, 'event/events.html', context)

@login_required
def rsvp_event(request, event_id):
    if request.method == 'POST':
        try:
            event = EventManager.objects.get(id=event_id)
        except EventManager.DoesNotExist:
            return JsonResponse({'status': 'fail', 'message': 'Event not found.'}, status=404)

        rsvp, created = RSVP.objects.get_or_create(event=event, user=request.user)
        if created:
            return JsonResponse({'status': 'success', 'username': request.user.username})
        else:
            return JsonResponse({'status': 'exists'})
    return JsonResponse({'status': 'fail'}, status=400)

@login_required
def event_detail(request, event_id):
    event = EventManager.objects.get(id=event_id)
    rsvps = event.rsvps.select_related('user').all()
    context = {
        'event': event,
        'rsvps': rsvps,
    }
    return render(request, 'event/event_detail.html', context)

@login_required
def delete_event(request, id):
    queryset = EventManager.objects.get(id=id)
    if queryset.user != request.user:
        return HttpResponseForbidden("Only the creator of this event may delete this event.")
    queryset.delete()
    return redirect('/')

@login_required
def update_event(request, id):
    queryset = EventManager.objects.get(id=id)
    if queryset.user != request.user:
        return HttpResponseForbidden("Only the creator of this event may make changes to this event.")
    
    if request.method == 'POST':
        data = request.POST
        event_image = request.FILES.get('event_image')
        event_name = data.get('event_name')
        event_description = data.get('event_description')
        event_time_str = data.get('event_time')
        

        queryset.event_name = event_name
        queryset.event_description = event_description

        if event_image:
            queryset.event_image = event_image

        if event_time_str:
            try:
                event_time = datetime.strptime(event_time_str, '%Y-%m-%dT%H:%M')
                queryset.event_time = event_time
            except ValueError:
                # Optionally handle invalid datetime input here
                pass
        
        queryset.save()
        return redirect('/')

    context = {'event': queryset}
    return render(request, 'event/update_event.html', context)