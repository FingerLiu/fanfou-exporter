#!/usr/bin/env python3

# export fanfou timeline to csv

import argparse
import time
import requests
import xlsxwriter
from bs4 import BeautifulSoup
import datetime
import pprint


default_homepage_url = "https://fanfou.com/bitcher"
default_cookie = "__utmc=208515845; __utmz=208515845.1648721440.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); uuid=3871ebcd18210725350e.1648721427.5; PHPSESSID=34jnkrgis2st4fg6jmlo514bp0; __utma=208515845.1228288682.1648721440.1651720913.1652595915.14; __utmv=208515845.self; msg=%E4%B8%BA%E4%BB%80%E4%B9%88%E4%B8%80%E4%B8%AA%E5%B0%8F%E5%8A%A8%E7%89%A9%E8%83%BD%E5%90%AC%E6%87%82%E2%80%9C%E6%8A%8A%E7%8B%97%E7%BB%B3%E5%8F%BC%E8%BF%87%E6%9D%A5%E2%80%9D%E5%91%A2%EF%BC%8C%E7%9C%9F%E7%A5%9E%E5%A5%87%E3%80%82; __utmt=1; __utmb=208515845.46.10.1652595915"
default_filepath = "./fanfou-{}.xlsx".format(datetime.datetime.now().strftime("%Y-%m-%d,_%H:%M:%S"))

parser = argparse.ArgumentParser(description='Export users timeline using your browser cookie.')
parser.add_argument('--homepage', default=default_homepage_url)
parser.add_argument('--cookie', default=default_cookie)
parser.add_argument('--filepath', default=default_filepath)
args = parser.parse_args()



# 构建 header 和 cookie
headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-language": "zh-CN,zh;q=0.9,ja;q=0.8,en-US;q=0.7,en;q=0.6,zh-TW;q=0.5",
    "cache-control": "max-age=0",
    "if-modified-since": "Sun, 15 May 2022 06:51:42 GMT",
    "sec-ch-ua": "\" Not A;Brand\";v=\"99\", \"Chromium\";v=\"101\", \"Google Chrome\";v=\"101\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"macOS\"",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "cookie": args.cookie,
    "Referrer-Policy": "strict-origin-when-cross-origin"
}

session = requests.Session()
session.headers = headers


with xlsxwriter.Workbook(args.filepath) as workbook:
    # add worksheet
    worksheet = workbook.add_worksheet()
    row = 0
    worksheet.write(row, 0, 'content')
    worksheet.write(row, 1, 'datetime')
    worksheet.write(row, 2, 'photo')

    # 请求第一页
    r = session.get(args.homepage)
    if r.status_code != 200:
        print("err fetch {}: {} {}", args.homepage, r.reason, r.status_code)
        exit(1)

    homepage = r.text
    soup = BeautifulSoup(homepage, 'html.parser')

    # get page count
    count = int(soup.find_all('ul', attrs={'class': 'paginator'})[0].find_all()[-1]['href'].split('.')[-1])

    # 遍历并写到文件
    for i in range(1, count + 1):
        print("scrap page {}".format(i))
        url = "{}/p.{}".format(args.homepage.strip("/"), i)
        r = session.get(url)
        if r.status_code != 200:
            print("err fetcch {}: {} {}", url, r.reason, r.status_code)
            exit(1)

        soup = BeautifulSoup(r.text, 'html.parser')
        stream = soup.find('div', attrs={"id": "stream"}).select('ol')[0].select('li')
        data = []
        for s in stream:
            d = dict()
            d['content'] = s.select_one('.content').text
            d['datetime'] = s.select_one('.time').text
            photo = s.select_one('.content').select_one('.photo')
            if photo:
                d['photo'] = photo['href']
            data.append(d)
        pprint.pprint(data)

        print("start write page {} to xlsx {}".format(i, args.filepath))
        for d in data:
            worksheet.write(row, 0, d['content'])
            worksheet.write(row, 1, d['datetime'])
            worksheet.write(row, 2, d.get('photo'))
            row += 1
        time.sleep(0.05)

    print("succeed.")

