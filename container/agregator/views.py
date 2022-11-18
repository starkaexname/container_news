from datetime import datetime
import requests
from bs4 import BeautifulSoup
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView
from .models import News, Category, Tag
from .forms import *
from django.contrib.auth import login, logout
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth.decorators import permission_required, login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .utils import myMixin
from django.core.cache import cache
from django.db.models import Q

current_date = datetime.now()
year = current_date.strftime('%Y')
month = current_date.strftime('%B').lower()


cat_dict = dict(Украина='https://korrespondent.net/all/ukraine/',
                Город='https://korrespondent.net/all/city/',
                Бизнес='https://korrespondent.net/all/business/',
                Мир='https://korrespondent.net/all/world/',
                Наука='https://korrespondent.net/all/tech/',
                Спорт='https://korrespondent.net/all/sport/',
                Шоубиз='https://korrespondent.net/all/showbiz/',
                LifestyleAndFashion='https://korrespondent.net/all/lifestyle/'
                )


def make_dict_from_db(dictall):
    clean_dict_1 = dict()
    for item in dictall:
        clean_dict_1[item.title] = item.pk
    return clean_dict_1


def make_set_from_db(setall):
    clean_set_1 = set()
    for item in setall:
        clean_set_1.add(item.content_url)
    return clean_set_1


def make_set_from_db2(setall):
    clean_set_2 = set()
    for item in setall:
        clean_set_2.add(item.tagarticle)
    return clean_set_2


def make_clear_time_2(published_at):
    nullindex = published_at.rindex(':')
    hours = int(published_at[nullindex - 2: nullindex])
    minutes = int(published_at[nullindex + 1: nullindex + 3])
    return hours, minutes


def get_korr(cat_link, cat_id, clean_news_set):
    day = current_date.day
    page = 1
    while day <= current_date.day:
        clean_link = (cat_link + year + '/' + month + '/' + str(day) + '/' + 'p' + str(page))
        print(clean_link)
        r = requests.get(clean_link).text
        soup = BeautifulSoup(r, 'lxml')
        posts = soup.find_all('div', class_="article__title")
        page += 1
        if len(posts):
            for post in posts:
                if not post.find('em'):
                    content_url = post.find('a').get('href')    # входной url новости
                    if content_url not in clean_news_set:
                        n = requests.get(content_url).text
                        soup = BeautifulSoup(n, 'lxml')
                        title = soup.find('h1', class_='post-item__title').text
                        tags = soup.find('div', class_='post-item__tags clearfix').find_all('a')
                        text_autor = 'Корреспондент.net'
                        try:
                            text_autor = soup.find('div', class_='post-item__info').find('a').text
                        except:
                            pass
                        finally:
                            published_at_soup = soup.find('div', class_='post-item__info').text
                            full_text = soup.find('div', class_='post-item__text').find_all('p')
                            preview_text = soup.find('div', class_='post-item__text').find('h2').text
                            photo_url = soup.find('div', class_='post-item__photo clearfix').find('img').get('src')
                            photo_src_name = ''
                            try:
                                photo_src_name = soup.find('div', class_='post-item__photo-author').text
                            except:
                                pass
                            finally:
                                views = soup.find('div', class_='post-item__views').text
                                hm = make_clear_time_2(published_at_soup)
                                published_at = datetime(year=current_date.year, month=current_date.month,
                                                        day=day, hour=hm[0], minute=hm[1], second=0)
                                # внесение в БД
                                n = News.objects.create(title=title, content_url=content_url, category_id=cat_id,
                                                        full_text=full_text, text_autor=text_autor,
                                                        published_at=published_at, photo_url=photo_url,
                                                        photo_src_name=photo_src_name, views=views,
                                                        preview_text=preview_text
                                                        )
                                clean_tag_set = make_set_from_db2(Tag.objects.all())
                                for i in tags:
                                    if i.text not in clean_tag_set:
                                        t = Tag.objects.create(tagarticle=i.text)
                                        n.tags.add(t)
                # else:
                #     break
        else:
            day += 1
            page = 1


def update_news():
    clean_cat_dict = make_dict_from_db(Category.objects.all())
    clean_news_set = make_set_from_db(News.objects.all())
    for item in cat_dict:
        Cat_id = clean_cat_dict.get(item)
        get_korr(cat_dict.get(item), Cat_id, clean_news_set)


update_news()


class NewsList(myMixin, ListView):
    model = News
    context_object_name = 'news'
    template_name = 'agregator/index.html'
    allow_empty = True
    paginate_by = 10

    def get_queryset(self):
        return News.objects.all().select_related('category')


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
    # pk_url_kwarg = 'pk'
    context_object_name = 'news_item'


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
        return News.objects.filter(category_id=self.kwargs['category_id']).\
            select_related('category')


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


# @login_required
@permission_required('agregator.test', login_url='login')
def admailto(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            mail = send_mail(form.cleaned_data['subject'], form.cleaned_data['full_text'],
                             'jbexname@gmail.com', ['bjexname@gmail.com', ], fail_silently=True)
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


# # обновление категорий в базе данных
# for item in cat_dict:
#     Category.objects.create(title=item)


    # def shownews(request):
    #     get_korr()
    #     context = {'korr_list': korr_list}
    #     return render(request, 'agregator/index.html', context)

# # cat parser
# def parse_categories():
#     link = 'https://ru.korrespondent.net/'
#     r = requests.get(link).text
#     soup = BeautifulSoup(r, 'lxml')
#     main_categories = soup.find_all('ul', class_="parts-unit")
#     for cat in main_categories:
#         cat_title = cat.find('a').text
#         Category.objects.create(title=cat_title)
#         # cat_url = cat.find('a').get('href')
#         # cat_dict.update({cat_title: cat_url})
# parse_categories()


# cat_dict['Украина'] = 'https://korrespondent.net/all/ukraine/'
# cat_dict['Город'] = 'https://korrespondent.net/all/city/'
# cat_dict['Бизнес'] = 'https://korrespondent.net/all/business/'
# cat_dict['Мир'] = 'https://korrespondent.net/all/world/'
# cat_dict['Наука'] = 'https://korrespondent.net/all/tech/'
# cat_dict['Спорт'] = 'https://korrespondent.net/all/sport/'
# cat_dict['Шоу-биз'] = 'https://korrespondent.net/all/showbiz/'
# cat_dict['Lifestyle&Fashion'] = 'https://korrespondent.net/all/lifestyle/'

#readyparser

#
# cat_dict = dict(Украина='https://korrespondent.net/all/ukraine/',
#                 Город='https://korrespondent.net/all/city/',
#                 Бизнес='https://korrespondent.net/all/business/',
#                 Мир='https://korrespondent.net/all/world/',
#                 Наука='https://korrespondent.net/all/tech/',
#                 Спорт='https://korrespondent.net/all/sport/',
#                 Шоубиз='https://korrespondent.net/all/showbiz/',
#                 LifestyleAndFashion='https://korrespondent.net/all/lifestyle/'
#                 )
#
#
# def make_clear_time(published_at):
#     unwanted = published_at.find('span')
#     unwanted.extract()
#     unwanted = published_at.find('a')
#     unwanted.extract()
#     linetosplit = published_at.text.strip().splitlines()
#     charstosplit = linetosplit[1].strip().split()
#     minsec = charstosplit[3]
#     minsec = minsec.split(sep=":")
#     hours = int(minsec[0])
#     minutes = int(minsec[1])
#     return hours, minutes
#
#
# def get_korr(cat_title, cat_link):
#     cat_id = Category.objects.get(title=cat_title).pk
#     current_date = datetime.now()
#     year = current_date.strftime('%Y')
#     month = current_date.strftime('%B').lower()
#     day = 1
#     page = 1
#     while day <= current_date.day:
#         clean_link = (cat_link + year + '/' + month + '/' + str(day) + '/' + 'p' + str(page))
#         print(clean_link)
#         r = requests.get(clean_link).text
#         soup = BeautifulSoup(r, 'lxml')
#         posts = soup.find_all('div', class_="article__title")
#         page += 1
#         if len(posts):
#             for post in posts:
#                 if post.find('em'):
#                     pass
#                 else:
#                     content_url = post.find('a').get('href')    # входной url новости
#                     n = requests.get(content_url).text
#                     soup = BeautifulSoup(n, 'lxml')
#                     title = soup.find('h1', class_='post-item__title').text
#                     text_autor = soup.find('div', class_='post-item__info').find('a').text
#                     published_at_soup = soup.find('div', class_='post-item__info')
#                     full_text = soup.find('div', class_='post-item__text').find_all('p')
#                     photo_url = soup.find('div', class_='post-item__photo clearfix').find('img').get('src')
#                     photo_src_name = soup.find('div', class_='post-item__photo-caption').text
#                     views = soup.find('div', class_='post-item__views').text
#                     hm = make_clear_time(published_at_soup)
#                     published_at = datetime(year=current_date.year, month=current_date.month,
#                                             day=day, hour=hm[0], minute=hm[1], second=0)
#                     # внесение в БД
#                     News.objects.create(title=title, content_url=content_url, category_id=cat_id,
#                                         full_text=full_text, text_autor=text_autor, published_at=published_at,
#                                         photo_url=photo_url, photo_src_name=photo_src_name, views=views
#                                         )
#         else:
#             day += 1
#             page = 1
#
# #
# # for item in cat_dict:
# #     get_korr(item, cat_dict.get(item))


# def make_clear_time(published_at):
#     unwanted = published_at.find('span')
#     unwanted.extract()
#     unwanted = published_at.find('a')
#     unwanted.extract()
#     linetosplit = published_at.text.strip().splitlines()
#     charstosplit = linetosplit[1].strip().split()
#     minsec = charstosplit[3]
#     minsec = minsec.split(sep=":")
#     hours = int(minsec[0])
#     minutes = int(minsec[1])
#     return hours, minutes