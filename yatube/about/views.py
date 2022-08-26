from django.views.generic.base import TemplateView


class AboutAuthorView(TemplateView):
    """Класс "Об авторе"."""
    template_name = 'about/author.html'


class AboutTechView(TemplateView):
    """Класс "Технологии"."""
    template_name = 'about/tech.html'
