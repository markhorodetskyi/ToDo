# from .tokens import account_activation_token
# from django.core.mail import EmailMessage
# from django.contrib.sites.shortcuts import get_current_site
# from django.template.loader import render_to_string
# from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
# from django.utils.encoding import force_bytes, force_text
# from django.contrib.auth import login
import logging
from datetime import date
from math import sqrt
from random import randint

import coloredlogs
from django.contrib import messages as html_msg
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.http import JsonResponse
from django.shortcuts import render, redirect, reverse
from django.views.generic import CreateView

from .forms import *
from .models import *

logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG')
coloredlogs.install(level='DEBUG', logger=logger)
coloredlogs.install(
    level='DEBUG', logger=logger,
    fmt='%(asctime)s.%(msecs)03d %(filename)s:%(lineno)d %(levelname)s | msg: "%(message)s"'
)


class CustomLoginView(LoginView):
    authentication_form = CustomAuthenticationForm


def home(request):
    return render(request, 'todolist/home.html', {})


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


def quadratic_equation(request):
    user_id = request.user
    arguments = EquationArgs.objects.filter(user=user_id).values('a1', 'a2', 'b1', 'b2', 'c1', 'c2').last()

    if request.method == 'POST':
        if "cancel" in request.POST:
            html_msg.warning(request, 'Скасовано')
            return redirect('home')
        else:
            form = RangeForm(request.POST)
            if form.is_valid():
                form.save()
                html_msg.success(request,
                               f'Успіх')
                return redirect('quadratic_equation')
            else:
                html_msg.error(request,
                               f'Помилка')
                return redirect('quadratic_equation')
    else:
        form = RangeForm({'user': request.user})

    """
    Код рішення ДЗ1 'квадратне рівняння' тут -------------------------------------------------------------------------
    """

    """
    розпаковка, у випадку якщо в бд нічого немає - одиниці
    """
    a1, a2, b1, b2, c1, c2 = arguments.values() if arguments else [1, 1, 1, 1, 1, 1]

    """
    міняємо місцями аргументи у випадку якщо хтось ввів спершу більший
    """
    a1, a2 = [a2, a1] if a1 > a2 else [a1, a2]
    b1, b2 = [b2, b1] if b1 > b2 else [b1, b2]
    c1, c2 = [c2, c1] if c1 > c2 else [c1, c2]

    data = {  # елемент django
        'a1': a1,
        'a2': a2,
        'b1': b1,
        'b2': b2,
        'c1': c1,
        'c2': c2,
        'results': [],
        'form': form,
    }

    if a2-a1 > 20 or b2-b1 > 20 or c2-c1 > 20:  # обмеження діапазону
        html_msg.error(request, f'Завеликий діапазон аргументів, максимум 20. Будь ласка зменшіть діапазон')  # Django
        return render(request, 'todolist/equation.html', data)  # Django

    """
    Тут є декілька запитань. пам'ятаю ти казав що лямбди будуть плюсом))) якщо лямбді присвоїти зміну, то на неї
    свариться РЕР8. Тож я зробив звичайну функцію. ну але лямбду правильніше використовувати анонімно, і можна б
    було запхати її в result_list.append, та я не ризикнув, він і так не читабельний. Але зато в одному рядку))
    """
    def discriminant(a, b, c): return (b * b) - 4 * a * c
    # discriminant = lambda a, b, c: (b * b) - 4 * a * c

    def root(a, b, c, d):
        return [round(((b * (-1)) - sqrt(d(a, b, c))) / 2 * a, 2), round(((b * (-1)) + sqrt(d(a, b, c))) / 2 * a, 2)]

    # root = lambda a, b, c, d: [round(((b * (-1)) - sqrt(d(a, b, c))) / 2 * a, 2),
    #                            round(((b * (-1)) + sqrt(d(a, b, c))) / 2 * a, 2)]
    result_list = []
    """
        Хотілось зробити повноцінний генератор і сходу згенерувати в result_list. Але мені заважає None в перевірці 
        дискримінанту. Прийшлось винести на зовні та користуватись append. Інакше всі None попадають в список. І
        костилі у вигляді '[[['. Не подобається мені це моє рішення. Пробував якось виправити за допомогою лямбда,
        та щось не складається в мене. Якщо є якись варіант був би радий побачити.
    """
    [[[result_list.append({'a': a, 'b': b, 'c': c, 'root': root(a, b, c, discriminant)}) if discriminant(a, b, c) >= 0
       else None for c in range(c1, c2)] for b in range(b1, b2)] for a in range(a1, a2)]

    """
        Якщо чесно, такий синтаксис мені більше підходить. але якщо б вдалось згенерувати зразу в ліст, я б віддав 
        перевагу першому варіанту. можливо ще щось прийде в голову.
    """
    # for a in range(a1, a2):
    #     for b in range(b1, b2):
    #         for c in range(c1, c2):
    #             result_list.append(f'a: {a}, b: {b}, c: {c}, YES {root(a, b, c, d)}')

    """
    Код рішення ДЗ1 квадратне рівняння кінець -------------------------------------------------------------------------
    """

    data['results'] = result_list  # Django
    html_msg.success(request, f'Знайдено {len(result_list)} рішень')  # Django
    return render(request, 'todolist/equation.html', data)  # Django


class CreateMatrix(CreateView):  # Django
    model = MatrixModel  # Django
    form_class = CreateMatrixForm  # Django
    template_name = 'todolist/forms.html'  # Django
    success_message = "Зміни збережено"  # Django

    def get_initial(self):
        initial = super().get_initial()
        initial['user'] = self.request.user
        return initial

    def get_success_url(self):
        return reverse('matrix')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        start = self.object.range_start
        end = self.object.range_end
        matrix_h = 15
        matrix_v = 10
        """
            Генератор матриці (знов той самий костиль) -------------------------------------------------------
            """
        self.object.matrix = [[randint(start, end) for i in range(matrix_h)] for a in range(matrix_v)]  # тут
        self.object.save()
        response = super(CreateMatrix, self).form_valid(form)
        return response

    def post(self, request, *args, **kwargs):
        if "cancel" in request.POST:
            html_msg.warning(request, 'Скасовано')
            return redirect('home')
        else:
            html_msg.success(request, 'Зміни успішно збережено')
            return super(CreateMatrix, self).post(request, *args, **kwargs)


def matrix_view(request):
    user_id = request.user
    matrix_param = MatrixModel.objects.filter(user=user_id).values('range_start', 'range_end', 'matrix').last()
    data = {
        'matrix': matrix_param['matrix'] if matrix_param else None
    }
    return render(request, 'todolist/matrix.html', data)


"""
    Код рішення ДЗ1 матриця тут -------------------------------------------------------------------------
    спрацьовує при натискані кнопки "знайти"
    Ті самі костилі))
    """


def find_number(request, number):
    user_id = request.user
    matrix_param = MatrixModel.objects.filter(user=user_id).values('range_start', 'range_end', 'matrix').last()
    matrix = matrix_param['matrix']
    rows = []
    column = []
    [rows.append(i) if number in e else None for i, e in enumerate(matrix)]
    [[column.append(i) if number == e else None for i, e in enumerate(matrix[row_index])] for row_index in rows]
    if request.is_ajax():
        return JsonResponse({'rows': list(map(lambda x: x + 1, rows)),  # добавляємо 1 для привильного відображення.
                             'column': list(set(map(lambda x: x + 1, column)))})  # те саме, тільки + очищаємо повтори.
    else:
        return JsonResponse({'status': None})


"""
    Код рішення ДЗ1 матриця кінець -------------------------------------------------------------------------
    """