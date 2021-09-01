from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from django.contrib.auth import login, authenticate
from account.forms import RegistrationForm, AccountUpdateForm
from django.urls import reverse_lazy
from django.views import generic

from account.models import Account


@login_required(login_url="/accounts/login")
def index(request):
    context = {
        "user": request.user
    }
    return render(request, template_name="account/profile.html", context=context)


def register_view(request, *args, **kwargs):
    user = request.user
    if user.is_authenticated:
        return HttpResponse(f"You are already authenticated as {user.email} <br> <a href='/accounts/logout'>Logout</a>"
                            f"<br><a href='/accounts/profile'>Profile</a>")
    context = {
        "user": user
    }
    if request.POST:
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get('email').lower()
            raw_password = form.cleaned_data.get('password1')
            account = authenticate(email=email, password=raw_password)
            login(request, account)
            destination = kwargs.get("next")
            if destination:
                return redirect(destination)
            return redirect("home")
        else:
            context['registration_form'] = form
    return render(request, 'registration/register.html', context=context)


@login_required(login_url="/accounts/login")
def edit_profile(request, *args, **kwargs):
    user = request.user
    user_id = kwargs.get('user_id')
    try:
        account = Account.objects.get(pk=user_id)
    except Account.DoesNotExist:
        return HttpResponse("Something went wrong!")
    if account.pk != request.user.pk:
        return HttpResponse("You cannot edit someone else's profile!")
    context = {}
    if request.POST:
        form = AccountUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("account:view", user_id=account.pk)
        else:
            form = AccountUpdateForm(request.POST, instance=request.user,
                                     initial={
                                         "id": account.pk,
                                         "email": account.email,
                                         "username": account.username,
                                         "profile_image": account.profile_image.url,
                                         "hide_email": account.hide_email
                                     })
    else:
        form = AccountUpdateForm(
                                 initial={
                                     "id": account.pk,
                                     "email": account.email,
                                     "username": account.username,
                                     "profile_image": account.profile_image.url,
                                     "hide_email": account.hide_email
                                 })
    context['form'] = form
    context['DATA_UPLOAD_MAX_MEMORY_SIZE'] = settings.DATA_UPLOAD_MAX_MEMORY_SIZE
    return render(request, 'account/edit.html', context=context)
