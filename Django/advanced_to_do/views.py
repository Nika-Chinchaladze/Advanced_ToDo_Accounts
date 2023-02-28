from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Users, Lists, Tasks
from .forms import ImageForm

# Create your views here.


def index_page(request):
    """returns login form"""
    dynamic_url = reverse("login-page")
    return HttpResponseRedirect(dynamic_url)


@login_required
def personal_page(request, my_list=None):
    """returns current users personal profile page"""
    chosen_list_tasks = []
    if request.method == "POST":
        if request.POST.get("list_item") == "list_item":
            present_user = Users.objects.get(email=request.user.email)
            check_list_by_name = Lists.objects.filter(
                list_name=request.POST["list_name"], user_id=present_user.id).first()
            if check_list_by_name is None:
                new_list = Lists(
                    list_name=request.POST["list_name"],
                    list_type="progress",
                    user_id=present_user
                )
                new_list.save()
                return HttpResponseRedirect(reverse("personal-page"))
            else:
                messages.error(
                    request, "List with that Name already exists in your account!")
                return HttpResponseRedirect(reverse("personal-page"))

        if request.POST.get("task_item") == "task_item":
            current_list_name = request.POST["task_parent"]
            current_list_object = Lists.objects.get(
                list_name=current_list_name)
            check_task_by_name = Tasks.objects.filter(
                task_name=request.POST["task_name"], list_id=current_list_object.id).first()
            if check_task_by_name is None:
                new_task = Tasks(
                    task_name=request.POST["task_name"],
                    list_id=current_list_object
                )
                new_task.save()
                return HttpResponseRedirect(reverse("personal-page"))
            else:
                messages.error(
                    request, "Task with that Name already exists in this List!")
                return HttpResponseRedirect(reverse("personal-page"))
    else:
        current_user = request.user
        current_user_info = Users.objects.get(email=current_user.email)
        users_completed_lists = Lists.objects.filter(
            user_id__id=current_user_info.id, list_type="completed")
        users_progress_lists = Lists.objects.filter(
            user_id__id=current_user_info.id, list_type="progress")
        if my_list is not None:
            result = Lists.objects.get(list_name=my_list)
            chosen_list_tasks = Tasks.objects.filter(list_id=result.id)
        return render(request, "advanced_to_do/personal.html", {
            "user": current_user,
            "user_image": current_user_info.user_image.url,
            "completed_lists": users_completed_lists,
            "progress_lists": users_progress_lists,
            "chosen_list": my_list,
            "chosen_tasks": chosen_list_tasks
        })


@login_required
def action_page(request, task_id):
    """return page, where user can delete or update conctere task"""
    if request.method == "POST":
        chosen_task = Tasks.objects.get(id=request.POST["id_task"])
        chosen_task.task_name = request.POST["name_task"]
        chosen_task.save()
        return HttpResponseRedirect(reverse("personal-page"))
    else:
        chosen_task = Tasks.objects.get(id=task_id)
        return render(request, "advanced_to_do/action.html", {
            "task": chosen_task
        })


# ========================================== CRUD OPERATIONS SECTION ====================================== #
@login_required
def delete_task(request, task_id):
    """deletes task from database that belongs to authenticated user"""
    chosen_task = Tasks.objects.get(id=task_id)
    chosen_task.delete()
    return HttpResponseRedirect(reverse("personal-page"))


@login_required
def delete_list(request, list_id):
    """deletes list from database that belongs to authenticated user"""
    chosen_list = Lists.objects.get(id=list_id)
    chosen_list.delete()
    return HttpResponseRedirect(reverse("personal-page"))


@login_required
def completed_list(request, list_id):
    """in-progress list will go into completed lists section"""
    chosen_list = Lists.objects.get(id=list_id)
    chosen_list.list_type = "completed"
    chosen_list.save()
    return HttpResponseRedirect(reverse("personal-page"))


@login_required
def progress_list(request, list_id):
    """completed list will go into in-progress lists section"""
    chosen_list = Lists.objects.get(id=list_id)
    chosen_list.list_type = "progress"
    chosen_list.save()
    return HttpResponseRedirect(reverse("personal-page"))


# =========================================== AUTHENTICATION SECTION ====================================== #
def register_page(request):
    """return registration page"""
    if request.method == "POST":
        form = ImageForm(request.POST, request.FILES)
        check_by_email = Users.objects.filter(
            email=request.POST["email"]).first()
        if check_by_email is None:
            if form.is_valid():
                form.save()

                new_user = User.objects.create_user(
                    username=f"{request.POST['first_name']} {request.POST['last_name']}",
                    email=request.POST["email"],
                    password=request.POST["password"]
                )
                new_user.save()

                user_name = f"{request.POST['first_name']} {request.POST['last_name']}"
                pass_word = request.POST["password"]
                user = authenticate(
                    request, username=user_name, password=pass_word)
                login(request, user)
                return HttpResponseRedirect(reverse("personal-page"))
        else:
            messages.error(request, "User Already Exists - Use another Email!")
            return HttpResponseRedirect(reverse("register-page"))
    else:
        form = ImageForm()
    return render(request, "advanced_to_do/register.html", {"form": form})


def login_page(request):
    """returns login page"""
    if request.method == "POST":
        user_name = request.POST["username"]
        pass_word = request.POST["password"]
        user = authenticate(request, username=user_name, password=pass_word)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("personal-page"))
        else:
            messages.error(
                request, "Please Enter Correct UserName and Password")
            return HttpResponseRedirect(reverse("login-page"))
    return render(request, "advanced_to_do/login.html")


def logout_page(request):
    """logs out user and returns login page"""
    logout(request)
    dynamic_url = reverse("login-page")
    return HttpResponseRedirect(dynamic_url)
