from django import template
from movies.models import Category, Movie

register = template.Library()


@register.simple_tag()
def get_categories():
    """Вывод всех категорий"""
    return Category.objects.all()

# Другим распространенным типом тега шаблона является тип, который отображает некоторые
# данные путем рендеринга другого шаблона. Регистрируем inclusion_tag и передаём в него
# тот шаблон, который мы Хотим что бы template_tag рендарил
@register.inclusion_tag('movies/last_movies.html')
def get_last_movies(sort = None):
    if not sort:
        movies = Movie.objects.order_by("-pk")[:2]
    else:
        movies = Movie.objects.filter(category__url = sort, draft=False).order_by("-pk")[:2]
    # if filter:
    # movies = Movie.objects.filter(category__url = "multfilmy", draft=False).order_by("-pk")[:2]
    # else :
    #     movies = Movie.objects.order_by("-pk")[:1]
    # Выбираем 5 записей из Movie. Сортировкой по pk. И присваиваем
    # movies список объектов заданной модели или по другому QuerySet
    return {"last_movies": movies}
