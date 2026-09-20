from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import re


def register(request):

    if request.method == "POST":

        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect("register")

        # Password validation
        if len(password) < 8:
            messages.error(
                request,
                "Password must be at least 8 characters long."
            )
            return redirect("register")

        if not re.search(r"[A-Z]", password):
            messages.error(
                request,
                "Password must contain at least one uppercase letter."
            )
            return redirect("register")

        if not re.search(r"[a-z]", password):
            messages.error(
                request,
                "Password must contain at least one lowercase letter."
            )
            return redirect("register")

        if not re.search(r"[0-9]", password):
            messages.error(
                request,
                "Password must contain at least one number."
            )
            return redirect("register")

        if not re.search(r"[!@#$%^&*]", password):
            messages.error(
                request,
                "Password must contain at least one special character."
            )
            return redirect("register")

        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        messages.success(request, "Account created successfully!")
        return redirect("login")

    return render(request, "register.html")

def login_view(request):

    if request.method == "POST":

        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect("home")

        messages.error(request, "Invalid username or password.")

    return render(request, "login.html")

@login_required
def profile(request):
    return render(request, "profile.html", {
        "user": request.user
    })

@login_required
def logout_view(request):
    logout(request)
    return redirect("home")

@login_required
def delete_account(request):

    if request.method == "POST":

        user = request.user

        logout(request)
        user.delete()

        return redirect("home")

    return render(request, "delete_account.html")