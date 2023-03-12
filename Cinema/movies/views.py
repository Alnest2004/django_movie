from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView
from django.views.generic.base import View

from . import verify
from .models import Movie, Category, Actor, Genre, Rating, Cinema
from .forms import ReviewForm, RatingForm, UserCreationForm, VerifyForm
from .utils import DataMixin


# Похож на Миксин
class GenreYear:
    """Жанры и года выхода фильмов"""

    def get_genres(self):
        return Genre.objects.all()

    def get_years(self):
        return Movie.objects.filter(draft=False).values("year").distinct().order_by("year")

class GenreRating:
    """Получаем все оценки"""
    def get_rating(self):
        return Rating.objects.filter(movie__url=self.kwargs["slug"])


class MoviesView(GenreYear, ListView):
    """Список фильмов"""
    # request - вся информация присланная от клиента(Браузера)
    model = Movie
    queryset = Movie.objects.all().filter(draft=False)
    template_name = "movies/movie_list.html"
    context_object_name = 'movie_list'

    paginate_by = 3

    # def get_context_data(self, *, object_list = None, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     c_def = self.get_user_context(title="Главная страница")
    #     context = dict(list(context.items()) + list(c_def.items()))
    #     return context


class CategoryView(GenreYear, ListView):
    model = Movie
    template_name = "movies/movie_list.html"
    context_object_name = 'movie_list'

    # тут мы выбираем определённые элементы из Movie
    def get_queryset(self):
        # category__url - category - название поля у Movies которое
        # ForeignKey. __url - означает что мы обращаемся к модели Category
        # и берём у этой модели url. self.kwargs['cat_slug'] - получаем slug
        # из header.html с помощью конструкции category.get_absolute_url
        return Movie.objects.filter(category__url=self.kwargs['cat_slug'], draft=False)


class MovieDetailView(GenreYear, GenreRating, DetailView):
    """Полное описание фильма"""
    model = Movie
    # slug_field Отвечает за то, по какому полю нужно будет искать нашу запись, в нашем
    # случаи это поле url. Эти данные будут переданы из url и сравнивая эти данные
    # с нашим полем, Django будет искать нужную нам запись
    slug_field = "url"
    queryset = Movie.objects.filter(draft=False)
    template_name = "movies/movie_detail.html"

    # метод get_context_data объединяет(сливает вместе) данные контекста
    # всех родительских классов с данными текущего класса.
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["star_form"] = RatingForm()
        context["form"] = ReviewForm()
        return context

    # def get_context_data(self, *, object_list=None, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     c_def = self.get_user_context(title="Детальное описание")
    #     context= dict(list(context.items())+ list(c_def.items()))
    #     return context


class AddReview(View):
    """Отзывы"""
    # GET будет обработан методом get(), запрос POST делегируется к post()

    # Используем метод post(это будет пост запрос http, принимая request,
    # pk - наше id фильма)
    # Тут получается приходят данные из пост запроса, которые мы получили из
    # form в movie_detail.html
    # pk - мы получаем из movie_detail.html строчкой movie.id
    def post(self, request, pk):
        form = ReviewForm(request.POST)
        movie = Movie.objects.get(id=pk)
        if form.is_valid():
            # commit = False - приостанавливаем хранение нашей формы
            form = form.save(commit=False)
            if request.POST.get("parent", None):
                form.parent_id = int(request.POST.get("parent"))

            # В поле movie, мы указываем фильм к которому нужно привязаться комент
            # Если посмотреть в бд то поле movie имеет название movie_id, которому
            # мы и присваиваем значение pk, связанного с ним комента
            # form.movie_id = pk
            form.movie = movie
            # сохроняется оно в модель reviews, потому что в forms.py мы прописали
            # модель которую будем использовать model = Reviews.
            form.save()
        return redirect(movie.get_absolute_url())


class ActorView(GenreYear, DetailView):
    """Вывод информации о режиссёре"""
    model = Actor
    template_name = 'movies/actor.html'
    # Бывает, что вам нужно добавить отображение к существующей модели.
    # Если в этой модели есть поле SlugField, но оно не называется slug,
    # и вы хотите создать адрес по этому полю, вам не нужно паниковать или
    # комбинировать. Просто переопределите атрибут slug_field.
    # ПОЛЕ ПО КОТОРОМУ МЫ БУДЕМ ИСКАТЬ НАШИХ АКТЕРОВ
    slug_field = "name"


class FilterMoviesView(GenreYear, ListView):
    """Фильтр фильмов(по годам)"""
    paginate_by = 2

    def get_queryset(self):
        # фильтруем там где года будут входить в список, который будет нам возвращаться с FRONTEND
        # это список наших годов. С помощью метода getlist мы из GET запроса
        # будем доставать все значения годов.
        # Q - ИНКАПУСЛЯЦИЯ
        queryset = Movie.objects.filter(
            Q(year__in=self.request.GET.getlist("year")) |
            Q(genres__in=self.request.GET.getlist("genre"))
        ).distinct()
        return queryset

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["year"] = ''.join([f"year={x}&" for x in self.request.GET.getlist("year")])
        context["genre"] = ''.join([f"genre={x}&" for x in self.request.GET.getlist("genre")])
        return context

# HttpRequest.META - Словарь Python содержащий все доступные HTTP заголовки
# запроса. Доступные заголовки зависят от сервера и клиента.
class AddStarRating(View):
    """Добавление рейтинга к фильму"""
    def get_client_ip(self, request):
        # HTTP_X_FORWARDED_FOR — содержит цепочку прокси адресов и последним
        # идёт IP непосредственного клиента обратившегося к прокси серверу.
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            # REMOTE_ADDR – IP-адрес клиента.
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def post(self, request):
        form = RatingForm(request.POST)
        if form.is_valid():
            Rating.objects.update_or_create(
                # будем получать ip адрес клиента, который отправил нам запрос
                ip = self.get_client_ip(request),
                # передаём поле movie(название которого мы указали в name в
                # movie_detail.html) и преобразуем в число. Эти данные
                # приходят из скрытого поля name=movie
                movie_id = int(request.POST.get("movie")),
                # передаём словарь, ключ того поля, которое мы хотим изменить
                # 'star_id' - название поля в БД в таблице Rating.
                # И значение на которое мы меняем, в том случаи если мы найдём
                # такую запись. Ключу star_id мы передаём значение с ключом star из нашего
                # POST запроса. star- название поля input, указанное в movie_detail.
                defaults={'star_id': int(request.POST.get("star"))}
            )
            return HttpResponseRedirect(reverse_lazy('home'))
        else:
            return HttpResponse(status=400)

class Search(ListView):
    """Поиск фильмов"""
    paginate_by = 2

    def get_queryset(self):
        # "q" - название поля <input> в sidebar.
        # title__icontains - фильтруем по полю title и принимаем дополнительный
        # параметр icontains, для того что бы у нас не учитывался регистр. И
        # затем сравниваем с self.request.GET.get("q") - те данные которые к нам
        # пришли в get запросу в q.
        # Если мы хотим преобразовать все буквы в нижний регистр, а
        # первую букву в верхний регистр, можно использовать метод capitalize()
        q = self.request.GET.get("q").capitalize()
        return Movie.objects.filter(title__icontains=q)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        # тут добавляем то значение которое к нам пришло, это нам нужно для того,
        # что бы у нас работала пагинация
        context["q"] = f'q={self.request.GET.get("q")}&'
        return context


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            # verify.send(form.cleaned_data.get('phone'))
            username = request.POST['username']
            password = request.POST['password1']
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('megaverify')
    else:
        form = UserCreationForm()
    return render(request, 'account/signup.html', {'form': form})


@login_required
def verify_code(request):
    if request.method == 'POST':
        form = VerifyForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data.get('code')
            if verify.check(request.user.phone, code):
                request.user.is_verified = True
                request.user.save()
                return redirect('home')
    else:
        form = VerifyForm()
    return render(request, 'account/verify.html', {'form': form})


class CinemasView(ListView):
    """Список фильмов"""
    # request - вся информация присланная от клиента(Браузера)
    model = Cinema
    queryset = Cinema.objects.all()
    template_name = "movies/cinema_list.html"
    context_object_name = 'cinema_list'

    paginate_by = 3

