# filepath: d:\New folder\three_step_auth\views.py
from django.shortcuts import render, redirect
from .forms import RegistrationForm
from django.contrib.auth.models import User
from django.contrib.auth import login

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            step1 = form.cleaned_data['step1']
            step2 = form.cleaned_data['step2']
            step3 = form.cleaned_data['step3']

            # Create the user
            user = User.objects.create_user(username=username)

            # Log the user in
            login(request, user)

            # Redirect to a success page
            return redirect('registration_successful')  # Replace with your success URL name
        else:
            return render(request, 'register.html', {'form': form})
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})

def registration_success(request):
    return render(request, 'registration_successful.html')