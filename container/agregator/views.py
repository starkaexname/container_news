from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView
from .models import Category, Tag
from .forms import *
from django.contrib.auth import login, logout
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .utils import myMixin
from django.core.cache import cache
from django.db.models import Q
from .tasks import updating
from .parser import update_news


class NewsList(myMixin, ListView):
    model = News
    context_object_name = 'news'
    template_name = 'agregator/index.html'
    allow_empty = True
    paginate_by = 10


    def get_queryset(self):

        return News.objects.select_related('category')


class Search(NewsList):
    paginate_by = 5

    def get_queryset(self):
        return News.objects.filter(Q(
            preview_text__icontains=self.request.GET.get('q')) | Q(
            title__icontains=self.request.GET.get('q'))).select_related('category')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['q'] = f"q={self.request.GET.get('q')}&"
        return context


class ViewNews(DetailView):
    model = News
    template_name = 'agregator/view_news.html'
    context_object_name = 'news_item'
    def get_queryset(self):
        return News.objects.select_related('category').prefetch_related('tags')

class CreateNews(LoginRequiredMixin, CreateView):
    form_class = NewsForm
    template_name = 'agregator/add_news.html'
    # success_url = reverse_lazy('homepage') по умолчанию используется redirect get_absolute_url из модели
    login_url = '/admin'
    # raise_exception = True


class CategoryNews(NewsList):
    template_name = 'agregator/category.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = str(Category.objects.get(pk=self.kwargs['category_id']))
        context['categories'] = cache.get_or_set('categories', Category.objects.all(), 15)
        return context

    def get_queryset(self):
        return News.objects.filter(category_id=self.kwargs['category_id']). \
            select_related('category')

class TagNews(NewsList):
    template_name = 'agregator/tag.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tag'] = str(Tag.objects.get(pk=self.kwargs['tag_id']))
        context['tags'] = cache.get_or_set('tags', Tag.objects.all(), 15)
        return context

    def get_queryset(self):
        return News.objects.filter(tags=self.kwargs['tag_id'])


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно')
            return redirect('homepage')
        else:
            messages.error(request, 'Ошибка регистрации')
    else:
        form = UserRegisterForm()
    return render(request, 'agregator/register.html', context={'form': form})


def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('homepage')
        else:
            messages.error(request, 'Ошибка входа')
    else:
        form = UserLoginForm()
    return render(request, 'agregator/login.html', context={'form': form})


def user_logout(request):
    logout(request)
    messages.success(request, 'Вы вышли из кабинета')
    return redirect('login')


@permission_required('agregator.test', login_url='login')
def admailto(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            mail = send_mail(form.cleaned_data['subject'], form.cleaned_data['full_text'],
                             '46346346346@gmail.com', ['346346346346@gmail.com', ], fail_silently=True)
            if mail:
                messages.success(request, 'Письмо успешно отправлено')
                return redirect('AdMailto')
            else:
                messages.error(request, 'Ошибка отправки')
        else:
            messages.error(request, 'Ошибка валидации')
    else:
        form = ContactForm()
    return render(request, 'agregator/test.html', context={'form': form})
