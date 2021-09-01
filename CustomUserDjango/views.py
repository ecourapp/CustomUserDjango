from django.contrib.auth.decorators import login_required
from django.shortcuts import render


# Create your views here.

def index(request):
    context = {
        "user": request.user
    }
    return render(request, template_name="home.html", context=context)
