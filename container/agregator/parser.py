from datetime import datetime
from .models import Category, Tag, News
import requests
from bs4 import BeautifulSoup


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


def make_clear_time_2(published_at):
    nullindex = published_at.rindex(':')
    hours = int(published_at[nullindex - 2: nullindex])
    minutes = int(published_at[nullindex + 1: nullindex + 3])
    return hours, minutes


def update_news():
    current_date = datetime.now()
    year = current_date.strftime('%Y')
    month = current_date.strftime('%B').lower()
    clean_cat_dict = make_dict_from_db(Category.objects.all())
    clean_news_set = set(News.objects.values_list('content_url', flat=True))
    for item in cat_dict:
        cat_id = clean_cat_dict.get(item)
        get_korr(cat_dict.get(item), cat_id, clean_news_set, year, month, current_date)


def get_korr(cat_link, cat_id, clean_news_set, year, month, current_date):
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
            pass
            for post in posts:
                if not post.find('em'):
                    content_url = post.find('a').get('href')
                    n = requests.get(content_url).text
                    soup = BeautifulSoup(n, 'lxml')
                    views = soup.find('div', class_='post-item__views').text
                    if content_url not in clean_news_set:
                        title = soup.find('h1', class_='post-item__title').text
                        tags = soup.find('div', class_='post-item__tags clearfix').find_all('a')
                        text_author = 'Корреспондент.net'
                        try:
                            text_author = soup.find('div', class_='post-item__info').find('a').text
                        except:
                            pass
                        finally:
                            published_at_soup = soup.find('div', class_='post-item__info').text
                            full_text = soup.find('div', class_='post-item__text').find_all('p')
                            full_text_str = ''
                            for p in full_text:
                                full_text_str += str(p)
                            preview_text = soup.find('div', class_='post-item__text').find('h2').text
                            photo_url = soup.find('div', class_='post-item__photo clearfix').find('img').get('src')
                            photo_src_name = ''
                            try:
                                photo_src_name = soup.find('div', class_='post-item__photo-author').text
                            except:
                                pass
                            finally:
                                hm = make_clear_time_2(published_at_soup)
                                published_at = datetime(year=current_date.year, month=current_date.month,
                                                        day=day, hour=hm[0], minute=hm[1], second=0)
                                # database objects creations
                                n = News.objects.create(title=title, content_url=content_url, category_id=cat_id,
                                                        full_text=full_text_str, text_author=text_author,
                                                        published_at=published_at, photo_url=photo_url,
                                                        photo_src_name=photo_src_name, views=views,
                                                        preview_text=preview_text
                                                        )
                                print(n)
                                clean_tag_set = set(Tag.objects.values_list('tagarticle', flat=True))
                                for i in tags:
                                    if i.text not in clean_tag_set:
                                        t = Tag.objects.create(tagarticle=i.text)
                                        n.tags.add(t)
                                    else:
                                        t2 = Tag.objects.get(tagarticle=i.text)
                                        n.tags.add(t2)
                    else:  # views count updating
                        c = News.objects.get(content_url=content_url)
                        c.views = views
                        c.save()
        else:
            day += 1
            page = 1

