#!/usr/bin/env python3

from pprint import pprint
import requests
from bs4 import BeautifulSoup
from user_agent import generate_user_agent
from itertools import groupby
import re
import time

user_agent = generate_user_agent(device_type="desktop", os="win")  # user agent generator

headers = {'User-Agent': user_agent}

pattern_mail = re.compile(r"^[\w\W]*?([a-zA-Z0-9]{1,100}[@][a-z]{2,25}\.[a-z]{2,15})")  # регулярное выражение для email
pattern_url = r"/^(https?:\/\/)?([\w\.]+)\.([a-z]{2,6}\.?)(\/[\w\.]*)*\/?$/"  # регулярное выражение для ссылок

test_url = "http://www.aptekanizkihcen.ua/"


def regex_mail(email):  # метод получения email  из строки
    result = re.findall(pattern_mail, email)
    return result


def regex_url(html):  # метод получения ссылок из строки
    result = re.findall(pattern_url, html)
    return result


def parse_link(link):  # парсер ссылок
    r = requests.get(link, headers=headers)
    if r.status_code != 200:
        print("Сайт {} не отвечает. Завершаем работу".format(link))
        return None
    html = r.text
    soup = BeautifulSoup(html, "lxml")
    link_list = []
    for row in soup.find_all('a', attrs={'href': re.compile("^http://")}):
        link_list.append(str(row.get('href')))
    return link_list


def parse_mail(html):  # парсер email
    soup = BeautifulSoup(html, "lxml")
    mail_list = []
    for row in soup.find_all('a', attrs={'href': re.compile("^mailto:")}):
        mail_list.extend(regex_mail(row.get('href')))
    return mail_list


if __name__ == '__main__':
    url = str(input("Сайт для парсинга: "))  #.replace("http://", "")

    urls = []
    urls_old = []
    mail_list = []
    url_new = []

    try:
        n = int(input("Глубина парсинга: "))
    except ValueError:
        print("Вы ввели НЕ число, посторите ввод.")
        n = int(input("Глубина парсинга, от 1 до -1 (больше 1 будет работать рекурсивно): "))

    """Если ввели не правильную цифру"""
    if n < 0:
        n = n * -1
    elif n == 0:
        n = 1

    """Далее определение поведения парсера работать рекурсивно или парсить данные только с одной ссылки"""
    if n != 1:
        try:
            urls = parse_link(url)
            if urls is None:
                exit()
        except requests.exceptions.MissingSchema:
            print("Ссылка '{}' работает. Проверьте правильность ввода и повторите ввод: ".format(url))
            url = str(input("\nСайт для парсинга: "))
            try:
                urls = parse_link(url)
            except requests.exceptions.MissingSchema:
                print("Ссылка не работает. Завершаем работу")
                exit()

        urls_old = urls.copy()
        urls = [i for i, _ in groupby(urls)]  # удаляем дубли
    else:
        urls.append(url)
        urls_old = urls.copy()

    """ Начинаем работу """
    for l in range(0, n):
        time_start = time.time()
        print("Уровень парсинга {}".format(l))
        len_start = len(urls)
        for u in range(len(urls)):
            link = urls.pop()
            html = requests.get(str(link), headers=headers).text  # получаем html-код страницы
            mail_list.extend(parse_mail(html))  # парсим електронные почты
            if n != 1:
                urls_new = parse_link(link)  # парсим новые урлы
                if urls_new is not None:
                    url_new.extend(urls_new)
                print("Проверено {}% ссылок.".format(round((len(urls) / len_start * 100), 2)))
            if n == 1:
                break

        for i in urls_old:  # чистим список спаршеных урлов от тех которые уже были в работе скрипта
            if i in url_new:
                url_new.remove(i)

        urls_old.extend(url_new)  # Добавляем новые урлы в список для отработаныых урлов
        urls.extend(url_new)  # добавлям новые урлы для парсинга
        urls = list(set(urls))  # удаляем дубли
        url_new.clear()
        t = round(((time.time() - time_start) / 60), 2)
        print("=" * 82)
        print("\nПрошли уровень парсинга {} за {} минуты. Спаршно {} електронных адресов.\n".format(l, t, len(mail_list)))
        print("=" * 82)

    print("Result: \n")
    pprint(mail_list)
