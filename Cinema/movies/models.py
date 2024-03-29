from datetime import date

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from ckeditor.fields import RichTextField


class Category(models.Model):
    """Категория"""
    name = models.CharField("Категория", max_length=150)
    description = models.TextField("Описание")
    url = models.SlugField(max_length=160, unique=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category', kwargs={"cat_slug": self.url})

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категория"


class Actor(models.Model):
    """Актёры и режиссёры"""
    name = models.CharField("Имя", max_length=100)
    age = models.PositiveSmallIntegerField("Возраст", default=0)
    description = models.TextField("Описание")
    image = models.ImageField("Изображение", upload_to="actors/")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Актёры и режиссеры"
        verbose_name_plural = "Актеры и режиссеры"

    def get_absolute_url(self):
        return reverse('actor_detail', kwargs={"slug" : self.name})


class Genre(models.Model):
    """Жанры"""
    name = models.CharField("Имя", max_length=100)
    description = models.TextField("Описание")
    url = models.SlugField(max_length=160, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"


class Movie(models.Model):
    """Фильмы"""
    title = models.CharField("Название", max_length=100)
    tagline = models.CharField("Слоган", max_length=100, default='')

    description = models.TextField("Описание")

    poster = models.ImageField("Постер", upload_to="movies/")
    year = models.PositiveSmallIntegerField("Дата выхода", default=2019)
    country = models.CharField("Страна", max_length=30)
    # Атрибут related_name указывает имя обратного отношения от модели Movie к вашей модели.
    # Если вы не укажете related_name, Django автоматически создаст его, используя имя вашей модели
    # с суффиксом _set, например Movie.map_set.all(). А с related_name будет  Movie.film_director.all()
    directors = models.ManyToManyField(Actor, verbose_name="режиссер", related_name="film_director")
    actors = models.ManyToManyField(Actor, verbose_name="актеры", related_name="film_actor")
    genres = models.ManyToManyField(Genre, verbose_name="жанры")
    world_premiere = models.DateField("Премьера в мире", default=date.today)
    budget = models.PositiveIntegerField("Бюджет", default=0, help_text="Указывать сумму в долларах")
    fess_in_usa = models.PositiveIntegerField(
        "Сборы в США", default=0, help_text="указывать сумму в долларах"
    )
    fess_in_world = models.PositiveIntegerField(
        "Сборы в мире", default=0, help_text="указывать сумму в долларах"
    )
    category = models.ForeignKey(
        Category, verbose_name="Категория", on_delete=models.SET_NULL, null=True
    )
    url = models.SlugField(max_length=130, unique=True)
    draft = models.BooleanField("Черновик", default=False)
    cinema = models.ManyToManyField("Cinema", verbose_name="Кинотеатр", related_name="movie_cinema", null=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        # movie_detail - наименование пути в urls.py. self.url - название
        # url которое берётся у данного класа. И затем мы передаём этот
        # параметр в slug, который затем подставляется в urls.py
        return reverse("movie_detail", kwargs={"slug": self.url})

    # будет возвращать список наших отзывов прикреплённых к фильму, фильтруя там где
    # поле parent Будет равно null, для этого мы пишем parent__isnull = True, благодаря
    # этому к нам вернутся только родительские отзывы к нашему фильму
    def get_review(self):
        return self.reviews_set.filter(parent__isnull = True)

    class Meta:
        verbose_name = "Фильм"
        verbose_name_plural = "Фильмы"

# movie.movieshots_set.all - Мы обращаемся к нашему объекту movie, затем к
# movieshots_set.all - ы забираем все связанные данные с этой моделью.
class MovieShots(models.Model):
    """Кадры из фильма"""
    title = models.CharField("Заголовок", max_length=100)
    description = models.TextField("Описание")
    image = models.ImageField("Изображение", upload_to="movie_shots/")
    movie = models.ForeignKey(Movie, verbose_name="Фильм", on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Кадр из фильма"
        verbose_name_plural = "Кадры из фильма"


class RatingStar(models.Model):
    """Звезда рейтинга"""
    value = models.SmallIntegerField("Значение", default=0)

    def __str__(self):
        return f'{self.value}'

    class Meta:
        verbose_name = "Звезда рейтинга"
        verbose_name_plural = "Звезды рейтинга"
        ordering = ["-value"]


class Rating(models.Model):
    """Рейтинг"""
    ip = models.CharField("IP адрес", max_length=15)
    star = models.ForeignKey(RatingStar, on_delete=models.CASCADE, verbose_name="звезда")
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, verbose_name="фильм")


    def __str__(self):
        return f"{self.star} - {self.movie}"

    class Meta:
        verbose_name = "Рейтинг"
        verbose_name_plural = "Рейтинги"


class Reviews(models.Model):
    """Отзывы"""
    email = models.EmailField()
    name = models.CharField("Имя", max_length=100)
    text = models.TextField("Сообщение", max_length=5000)
    parent = models.ForeignKey(
        'self', verbose_name="Родитель", on_delete=models.SET_NULL, blank=True, null=True
    )
    movie = models.ForeignKey(Movie, verbose_name="фильм", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} - {self.movie}"

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"


class Employees(models.Model):
    """Работники"""
    STATUS_CHOICES = [
        ('cinema_manager', 'Cinema Manager'),
        ('accountant', 'Accountant'),
        ('booker', 'Booker'),
        ('adversting_and_marketing_manager', 'Advertising and Marketing Manager'),
        ('film_engineer', 'Film engineer'),
        ('projectionist', 'Projectionist'),
        ('administrator', 'Administrator'),
        ('controllers', 'Controllers'),
        ('senior_cashier', 'Senior cashier'),
        ('cashiers', 'Cashiers'),
        ('bartenders', 'Bartenders'),
        ('cleaner', 'Cleaner'),
        ('security_guard', 'Security guard'),
        ('unknown', 'Unknown'),
    ]
    status = models.CharField("Статус", max_length=50, choices=STATUS_CHOICES, default="unknown", )
    FIO = models.CharField("ФИО", max_length=100)
    Number = models.CharField("Номер телефона", max_length=30)
    address = models.CharField("Адрес", max_length=100)

    def __str__(self):
        return f"{self.FIO} - {self.status}"

    class Meta:
        verbose_name = "Работник"
        verbose_name_plural = "Работники"


class Supplier_list(models.Model):
    name = models.CharField("Название поставщика", max_length=50)
    address = models.CharField("Адрес поставщика", max_length=100)

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = "Поставщик"
        verbose_name_plural = "Поставщики"


class Cinema(models.Model):
    name = models.CharField("Название кинотеатра", max_length=50)
    image = models.ImageField("Изображение", upload_to="cinema/", null=True)
    address = models.CharField("Адрес кинотеатра", max_length=100)
    number = models.CharField("Номер телефона кинотеатра", max_length=30)
    employee = models.ManyToManyField(Employees, verbose_name="работник", related_name="cinema_employee")
    supplier = models.ManyToManyField(Supplier_list, verbose_name="поставщик", related_name="cinema_supplier")

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = "Кинотеатр"
        verbose_name_plural = "Кинотеатры"



class User(AbstractUser):
    phone = models.CharField(max_length=20, blank=False)
    is_verified = models.BooleanField(default=False)

