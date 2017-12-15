#coding:utf-8
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect
from django.views.generic import FormView, TemplateView, DetailView, CreateView, \
    DeleteView, UpdateView

from proto.forms import PhotographerForm, PhotoUploadForm, UserPanelForm, \
    PhotoUpdateForm
from proto.models import Category, Photo
from .common import LoginRestrictedView, MultiFormsView


class PersonalSettings(LoginRestrictedView, MultiFormsView):
    template_name = 'settings/personal_details.html'
    form_classes = {'form': PhotographerForm, 'form_user': UserPanelForm}
    success_url = reverse_lazy('settings_personal')

    def get_form_kwargs(self, form_name, bind_form=False):
        kwargs = super(PersonalSettings, self).get_form_kwargs(form_name, bind_form)
        kwargs['instance'] = self.request.user.photographer \
            if form_name == 'form' else self.request.user
        return kwargs

    def forms_valid(self, forms, *args, **kwargs):
        # multi form functionality
        list([form.save() for (name, form) in forms.items()])
        return super(PersonalSettings, self).forms_valid(forms, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(PersonalSettings, self).get_context_data(**kwargs)
        context.update({
            'js_handler': 'personal_details'
        })
        return context



class ScoreBoard(LoginRestrictedView, TemplateView):
    template_name = 'settings/scoreboard.html'

    def get_context_data(self, **kwargs):
        context = super(ScoreBoard, self).get_context_data(**kwargs)
        context['p'] = self.request.user.photographer
        return context


class Portfolio(LoginRestrictedView, TemplateView):
    template_name = 'settings/portfolio.html'

    def get_context_data(self, **kwargs):
        context = super(Portfolio, self).get_context_data(**kwargs)
        context['photos'] = self.request.user.photographer.active_photos().count()
        context['top_photos'] = self.request.user.photographer.top_photos()
        categories = self.request.user.photographer.active_categories()
        context['categories'] = [
            (category,
             self.request.user.photographer.category_photos(category).count())
            for category in categories
        ]
        return context


class CategoryDetail(LoginRestrictedView, DetailView):
    model = Category
    template_name = 'settings/category.html'
    context_object_name = 'category'

    def get_queryset(self):
        return self.request.user.photographer.active_categories()

    def get_context_data(self, **kwargs):
        context = super(CategoryDetail, self).get_context_data(**kwargs)
        context['photos'] = \
            self.request.user.photographer.category_photos(self.get_object())
        return context


class Upload(LoginRestrictedView, CreateView):
    template_name = 'settings/upload.html'
    model = Photo
    form_class = PhotoUploadForm
    success_url = reverse_lazy('settings_portfolio')

    def get_context_data(self, **kwargs):
        context = super(Upload, self).get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.photographer = self.request.user.photographer
        instance.save()
        form.save_m2m()
        return HttpResponseRedirect(self.success_url)


class Update(LoginRestrictedView, UpdateView):
    template_name = 'settings/update.html'
    model = Photo
    form_class = PhotoUpdateForm
    success_url = reverse_lazy('settings_portfolio')

    def get_queryset(self):
        return self.request.user.photographer.active_photos()

    def get_context_data(self, **kwargs):
        context = super(Update, self).get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.photographer = self.request.user.photographer
        instance.save()
        form.save_m2m()
        return HttpResponseRedirect(self.success_url)


class Delete(LoginRestrictedView, DeleteView):
    template_name = 'settings/deletephoto.html'
    model = Photo
    success_url = reverse_lazy('settings_portfolio')

    def get_queryset(self):
        return self.request.user.photographer.active_photos()
