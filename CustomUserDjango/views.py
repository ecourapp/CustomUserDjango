from django.contrib.auth.decorators import login_required
from django.shortcuts import render


# Create your views here.

@login_required(login_url="/accounts/login")
def index(request):
    context = {
        "user": request.user
    }
    return render(request, template_name="home.html", context=context)
