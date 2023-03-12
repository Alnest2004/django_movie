from django.contrib import admin
from django import forms
from django.contrib.admin import ModelAdmin
from django.utils.safestring import mark_safe

from .models import *
from ckeditor_uploader.widgets import CKEditorUploadingWidget



class MovieAdminForm(forms.ModelForm):
    """Форма с виджетом ckeditor"""
    description_ru = forms.CharField(label="Описание", widget=CKEditorUploadingWidget())

    class Meta:
        model = Movie
        fields = '__all__'



@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    """Категории"""
    # list_display указывает какие поля отображать на странице списка объектов.
    list_display = ("id", "name", "url")
    list_display_links = ("name",)
    prepopulated_fields = {"url": ("name",)}

# При открытии записи нашего фильма мы видели все отзывы, которые прикреплены к данному
# фильму, это делает данный класс.
# Если вы хотите редактировать и добавлять объекты Image на странице
# добавления/редактирования объектов Product, вы можете использовать GenericStackedInline
"""
class StackedInline(выводит в строках) и TabularInline(выводит в столбцах)
Интерфейс администратора позволяет редактировать связанные объекты на одной
странице с родительским объектом. Это называется “inlines”. Например, у нас есть
две модели:
"""
class ReviewInLine(admin.TabularInline):
    """Отзывы на странице фильма"""
    model = Reviews
    # Указывает количество дополнительных полей
    extra = 1
    # указываем поля которые будут только для чтения
    readonly_fields = ("name", "email")


# Выводим те данные которые привязаны к данной модели MovieShots
class MovieShotsInLine(admin.TabularInline):
    model = MovieShots
    extra = 1
    readonly_fields = ("get_image", )
    def get_image(self, obj):
        if obj.image:
            return mark_safe(f'<img src={obj.image.url} width="100" height="110" ')

    get_image.short_description = "Изображение"


@admin.register(Movie)
class MovieAdmin(ModelAdmin):
    """Фильмы"""
    list_display = ("title", "draft")


    # list_display = ("title", "category", "url", "draft")
    list_filter = ("category", "year")
    search_fields = ("title", "category__name")
    inlines = [MovieShotsInLine, ReviewInLine]
    save_on_top = True
    save_as = True
    list_editable = ("draft", )
    actions = ["publish", "unpublish"]
    # form = MovieAdminForm
    readonly_fields = ("get_image", )

    fieldsets = (
        (None, {
            "fields": (("cinema"),)
        }),
        (None, {
            "fields": (("title", "tagline"), )
        }),
        (None, {
            "fields": ("description", ("poster", "get_image"))
        }),
        (None, {
            "fields": (("year", "world_premiere", "country"),)
        }),
        ("Актёры", {
            "classes": ("collapse ",),
            "fields": (("actors", "directors", "genres", "category"),)
        }),
        (None, {
            "fields": (("budget", "fess_in_usa", "fess_in_world"),)
        }),
        ("Options", {
            "fields": (("url", "draft"),)
        }),
    )



    def get_image(self, obj):
        return mark_safe(f'<img src={obj.poster.url} width="100" height="110" ')

    # QuerySet, по сути, — список объектов заданной модели. QuerySet
    # позволяет читать данные из базы данных, фильтровать и изменять их порядок.
    def unpublish(self, request, queryset):
        """Снять с публикации"""
        # тут мы снимаем с публикации выбранные элементы
        row_update = queryset.update(draft=True)
        # Далее проверяем сколько записей было обновлено
        if row_update == 1:
            message_bit = "1 запись была обновлена"
        else:
            message_bit = f"{row_update} записей были обновлены"
        # тут мы выводим сообщение в админку после обновления
        self.message_user(request, f"{message_bit}")

    def publish(self, request, queryset):
        """Опубликовать"""
        row_update = queryset.update(draft=False)
        if row_update == 1:
            message_bit = "1 запись была обновлена"
        else:
            message_bit = f"{row_update} записей были обновлены"
        self.message_user(request, f"{message_bit}")

    publish.short_description = "Опубликовать"
    publish.allowed_permissions = {'change', }

    unpublish.short_description = "Снять с публикации"
    unpublish.allowed_permissions = {'change', }

    get_image.short_description = "Изображение"


@admin.register(Reviews)
class ReviewAdmin(admin.ModelAdmin):
    """Отзывы"""
    list_display = ("name", "email", "parent", "movie", "id")
    # поля только для чтения(то есть нельзя редактировать)
    readonly_fields = ("name", "email")


@admin.register(Genre)
class GenreAdmin(ModelAdmin):
    """Жанры"""
    list_display = ("name", "url")



@admin.register(Actor)
class ActorAdmin(ModelAdmin):
    """Актёры"""
    list_display = ("name", "age", "get_image")
    readonly_fields = ("get_image", )

    # принимает модель объекта актёров
    def get_image(self, obj):
        # mark_safe - выведет html не как строку, а как тег
        if obj.image:
            return mark_safe(f'<img src={obj.image.url} width="50" height="60" ')

    get_image.short_description = "Изображение"


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    """Рейтинг"""
    list_display = ("star", "movie", "ip")


@admin.register(MovieShots)
class MovieShotsAdmin(ModelAdmin):
    """Кадры из фильма"""
    list_display = ("title", "movie", "get_image")
    readonly_fields = ("get_image",)

    def get_image(self, obj):
        if obj.image:
            return mark_safe(f'<img src={obj.image.url} width="50" height="60" ')

    get_image.short_description = "Изображение"


@admin.register(Employees)
class EmployeesAdmin(admin.ModelAdmin):
    """Работники"""
    list_display = ("status", "FIO", "Number", "address")
    list_filter = ("status", "FIO")
    search_fields = ("status", "FIO")


@admin.register(Supplier_list)
class Supplier_listAdmin(admin.ModelAdmin):
    """Поставщики"""
    list_display = ("name", "address")
    list_filter = ("address", "name")
    search_fields = ("address", "name")


@admin.register(Cinema)
class CinemaAdmin(admin.ModelAdmin):
    """Кинотеатры"""
    list_display = ("name", "address", "number")
    list_filter = ("name",)
    search_fields = ("name",)

    fieldsets = (
        (None, {
            "fields": (("name", "address", "number"),)
        }),
        (None, {
            "fields": (("image",),)
        }),
        (None, {
            "fields": (("employee", "supplier"),)
        }),
    )

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Пользователи"""
    list_display = ("username", "phone", "is_verified")

admin.site.register(RatingStar)
# admin.site.register(Reviews)

admin.site.site_title = "Django Movies"
admin.site.site_header = "Django Movies"

