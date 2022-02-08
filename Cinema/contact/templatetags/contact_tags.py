from django import template
from contact.forms import ContactForm

# иблиотека тегов должна содержать переменную register равную экземпляру
# django.template.Library, в которой регистрируются все определенные теги и фильтры.
register = template.Library()

# который отображает некоторые
# данные путем рендеринга другого шаблона. Регистрируем inclusion_tag и передаём в него
# тот шаблон, который мы Хотим что бы template_tag рендарил
@register.inclusion_tag("contact/tags/form.html")
def contact_form():
    # возвращаем нашу контактную форму
    return {"contact_form": ContactForm()}
