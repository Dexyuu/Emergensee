from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from Account.forms import AccountAuthenticationForm
from django.contrib import messages

# Create your views here.

def login_view(request):
    context = {}
    if request.POST:
        form = AccountAuthenticationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user:
                if user.is_superuser:
                    login(request, user)
                    return redirect('Home')  # Redirect to a home page or dashboard
                else:
                    messages.error(request, 'You do not have the permission to access this page')
            else:
                messages.error(request, 'Invalid username or password')
    else:
        form = AccountAuthenticationForm()
    context['login_form'] = form
    return render(request, 'login/home.html', context)