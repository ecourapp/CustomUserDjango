import math

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from django.contrib.auth import login, authenticate
from account.forms import RegistrationForm, AccountUpdateForm
from django.urls import reverse_lazy
from django.views import generic
from django.core.files.storage import default_storage
from django.core.files.storage import FileSystemStorage
import os
import cv2
import json
import base64
import requests
from django.core import files

from account.models import Account

TEMP_PROFILE_IMAGE_NAME = "temp_profile_image.png"


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


def save_temp_profile_image_from_base64(image_string, user):
    INCORRECT_PADDING_EXCEPTION = "Incorrect padding"
    directory = settings.TEMP_DIR
    try:
        if not os.path.exists(directory):
            os.mkdir(directory)
        if not os.path.exists(directory + "/" + str(user.pk)):
            os.mkdir(directory + "/" + str(user.pk))
        url = os.path.join(directory + "/" + str(user.pk), TEMP_PROFILE_IMAGE_NAME)
        storage = FileSystemStorage(location=url)
        image = base64.b64decode(image_string)
        with storage.open('', 'wb+') as destination:
            destination.write(image)
            destination.close()
        return url
    except Exception as e:
        if str(e) == INCORRECT_PADDING_EXCEPTION:
            image_string += "=" * ((4 - len(image_string) % 4) % 4)
            return save_temp_profile_image_from_base64(image_string, user)


def set_float(data):
    floated = float(data)
    number = int(floated)
    return number


@login_required(login_url="/accounts/login")
def crop_image(request, *args, **kwargs):
    payload = {}
    user_email = request.user.email
    user = Account.objects.get(email=user_email)
    if request.POST and user.is_authenticated:
        try:
            image_string = request.POST.get("image")
            url = save_temp_profile_image_from_base64(image_string, user)
            print(f"url: {url}")
            img = cv2.imread(url)

            crop_x = set_float(data=request.POST.get("cropX"))
            crop_y = set_float(data=request.POST.get("cropY"))
            crop_width = set_float(data=request.POST.get("cropWidth"))
            crop_height = set_float(data=request.POST.get("cropHeight"))
            if crop_x < 0:
                crop_x = 0
            if crop_y < 0:  # There is a bug with cropperjs. y can be negative.
                crop_y = 0
            crop_img = img[crop_y:crop_y + crop_height, crop_x:crop_x + crop_width]

            cv2.imwrite(url, crop_img)

            # delete the old image
            user.profile_image.delete()

            # Save the cropped image to user model
            user.profile_image.save("profile_image.png", files.File(open(url, 'rb')))
            user.save()

            payload['result'] = "success"
            payload['cropped_profile_image'] = user.profile_image.url

            # delete temp file
            os.remove(url)

        except Exception as e:
            payload['result'] = "error"
            payload['exception'] = str(e)
            raise e
    return HttpResponse(json.dumps(payload), content_type="application/json")

