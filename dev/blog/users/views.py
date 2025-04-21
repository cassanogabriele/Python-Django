# users/views.py
from django.shortcuts import render, redirect
from .forms import RegistrationForm
from django.contrib.auth import authenticate, login

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()  # Cela enregistre l'utilisateur, y compris l'email dans la table auth_user
            username = form.cleaned_data['username']
            lastname = form.cleaned_data['last_name']
            firstname = form.cleaned_data['first_name']
            password = form.cleaned_data['password1']      
            email = form.cleaned_data['email']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('blog-home')
    else:
        form = RegistrationForm()

    context = {'form': form}
    return render(request, 'users/register.html', context)

