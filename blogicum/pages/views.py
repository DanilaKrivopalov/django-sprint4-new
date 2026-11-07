from django.http import HttpResponse
from django.template import loader
from django.views.generic import TemplateView


class AboutView(TemplateView):
    template_name = 'pages/about.html'


class RulesView(TemplateView):
    template_name = 'pages/rules.html'


def csrf_failure(request, reason=''):
    template = loader.get_template('pages/403csrf.html')
    return HttpResponse(
        template.render({'reason': reason}, request),
        status=403,
    )


def page_not_found(request, exception):
    template = loader.get_template('pages/404.html')
    return HttpResponse(
        template.render(request=request),
        status=404,
    )


def server_error(request):
    template = loader.get_template('pages/500.html')
    return HttpResponse(
        template.render(request=request),
        status=500,
    )
