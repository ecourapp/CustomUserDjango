from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect


# Create your views here.

def index(request):
    if request.user:
        if request.user.is_authenticated:
            return redirect('account:view')
    context = {
        "user": request.user
    }
    return render(request, template_name="home.html", context=context)
