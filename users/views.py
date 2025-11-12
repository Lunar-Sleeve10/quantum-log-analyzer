from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.shortcuts import render, redirect

def login_signup_page(request):
    login_form = AuthenticationForm()
    signup_form = UserCreationForm()

    if request.method == 'POST':
        # Check if the login form was submitted
        if 'login_submit' in request.POST:
            login_form = AuthenticationForm(request, data=request.POST)
            if login_form.is_valid():
                username = login_form.cleaned_data.get('username')
                password = login_form.cleaned_data.get('password')
                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request, user)
                    return redirect('home')
        
        # Check if the sign-up form was submitted
        elif 'signup_submit' in request.POST:
            signup_form = UserCreationForm(request.POST)
            if signup_form.is_valid():
                user = signup_form.save()
                login(request, user)
                return redirect('home')
    
    context = {
        'login_form': login_form,
        'signup_form': signup_form
    }
    return render(request, 'registration/login.html', context)