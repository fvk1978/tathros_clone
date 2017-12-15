# coding:utf-8
from django.views.generic import TemplateView


class FAQ(TemplateView):
    template_name = 'proto/faq.html'


class Info(TemplateView):
    template_name = 'proto/info.html'


class Contact(TemplateView):
    template_name = 'proto/contact.html'


class Terms(TemplateView):
    template_name = 'proto/agb.html'


class Privacy(TemplateView):
    template_name = 'proto/privacy.html'


class Impressum(TemplateView):
    template_name = 'proto/impressum.html'

