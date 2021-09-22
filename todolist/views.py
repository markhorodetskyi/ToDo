# from .tokens import account_activation_token
# from django.core.mail import EmailMessage
# from django.contrib.sites.shortcuts import get_current_site
# from django.template.loader import render_to_string
# from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
# from django.utils.encoding import force_bytes, force_text
# from django.contrib.auth import login

from django.shortcuts import render, redirect
from django.contrib import messages as html_msg
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from datetime import date
from .forms import *
from .models import *


class CustomLoginView(LoginView):
    authentication_form = CustomAuthenticationForm


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            for checkEmail in User.objects.all().values('email'):
                if checkEmail['email'] == form.data['email']:
                    html_msg.warning(request, f'Така електронна адреса вже зареєстрована')
                    return redirect('signup')
            user = form.save(commit=False)
            user.is_active = True
            user.save()
            # current_site = get_current_site(request)
            # mail_subject = 'Підтвердження електроного адресу'
            # message = render_to_string('todolist/acc_active_email.html', {
            #     'user': user,
            #     'domain': current_site.domain,
            #     'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            #     'token': account_activation_token.make_token(user),
            # })
            # to_email = form.cleaned_data.get('email')
            # EmailMessage()
            # email = EmailMessage(
            #     subject=mail_subject, body=str(message), to=[to_email]
            # )
            # print(to_email)
            # print(message)
            # try:
            #     email.send()
            # except Exception as e:
            #     print(e)
            #     html_msg.warning(request,
            #                      f'Сталась неочікувана помилка, будь ласка спробуйте ще раз')
            #     return redirect('signin')
            username = form.cleaned_data.get('username')
            html_msg.success(request,
                             f'Користувач {username}, був успішно створений.')
            return redirect('signin')
    else:
        form = SignUpForm()
    return render(request, 'todolist/signup.html', {'form': form})


# def activate(request, uidb64, token):
#     print(force_text(urlsafe_base64_decode(uidb64)))
#     try:
#         uid = force_text(urlsafe_base64_decode(uidb64))
#         user = User.objects.get(pk=uid)
#         print(uid, user)
#     except(TypeError, ValueError, OverflowError, User.DoesNotExist):
#         user = None
#     if user is not None and account_activation_token.check_token(user, token):
#         user.is_active = True
#         user.save()
#         login(request, user)
#         # return redirect('home')
#         username = user.username
#         html_msg.success(request, f'Користувач {username}, був успішно активований.')
#         return redirect('signin')
#     else:
#         html_msg.error(request, f'Це посилання не дійсне.')
#         return redirect('signin')


@login_required(login_url='signin')
def end_task(request, pk):
    try:
        Todo.objects.filter(id=pk).update(complete=True)
        html_msg.success(request,
                         f'Завдання завершено')
        return redirect('home')
    except:
        html_msg.error(request, f'Сталась неочікувана помилка, будь ласка спробуйте ще раз')
        return redirect('home')


@login_required(login_url='signin')
def add_task(request):
    user_id = request.user
    # tasks = get_task_dict(user_id)
    tasks = Todo.objects.filter(user=user_id)
    form = TaskForm()
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            new_entry = Todo(user_id=user_id.pk,
                             title=form.data['title'],
                             description=form.data['description'],
                             priority=form.data['priority'],
                             complete=False,
                             ended_at=form.data['ended_at'])
            new_entry.save()
            html_msg.success(request, 'New task added')
            return redirect('home')
        else:
            html_msg.warning(request,
                             f'Помилка')
            return redirect('home')
    data = {'tasks': tasks, 'form': form}
    unfinished = 0
    for task in tasks:
        days = task.ended_at - date.today()
        if days.days <= 3:
            html_msg.error(request, f'task - ({task.title}) will be ended during {days.days} days')
        if not task.complete:
            unfinished += 1
    html_msg.warning(request, f'You have {unfinished} unfinished tasks')
    return render(request, 'todolist/addTask.html', data)
