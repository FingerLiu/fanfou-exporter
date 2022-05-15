#!/usr/bin/env python3

# export fanfou timeline to csv

import os
import argparse
import time
import requests
import xlsxwriter
from bs4 import BeautifulSoup
import datetime
import pprint
import random
from io import BytesIO

default_homepage_url = "https://fanfou.com/bitcher"
default_cookie = "__utmc=208515845........."

parser = argparse.ArgumentParser(description='Export users timeline using your browser cookie.')
parser.add_argument('--homepage', default=default_homepage_url)
parser.add_argument('--cookie', default=default_cookie)
parser.add_argument('--filepath', default='')
parser.add_argument('--start_page', default=1, type=int)
args = parser.parse_args()

name = args.homepage.strip('/').split('/')[-1]

if not args.filepath:
    filepath = "./fanfou-{}-{}.xlsx".format(name, datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S"))
else:
    filepath = args.filepath

photo_dir = "./{}-photos".format(name)

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


with xlsxwriter.Workbook(filepath) as workbook:
    # add worksheet
    worksheet = workbook.add_worksheet()
    row = 0
    worksheet.write(row, 0, 'datetime')
    worksheet.write(row, 1, 'content')
    worksheet.write(row, 2, 'link')
    worksheet.write(row, 3, 'preview')
    worksheet.write(row, 4, 'photo')
    worksheet.write(row, 5, 'photo_raw_link')
    worksheet.set_column(0, 0, 18)
    worksheet.set_column(1, 1, 120)
    worksheet.set_column(2, 2, 40)
    worksheet.set_column(3, 3, 20)
    worksheet.set_column(4, 4, 50)
    worksheet.set_column(5, 5, 100)
    row += 1
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
    for i in range(args.start_page, count + 1):
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
            d['datetime'] = s.select_one('.time').text
            d['content'] = s.select_one('.content').text
            link = s.select_one('.content').select_one('a:not(.photo)')
            if link:
                d['link'] = link['href']
            photo = s.select_one('.content').select_one('.photo')
            if photo:
                d['photo'] = photo['href']
                d['preview'] = photo.select_one('img')['src']
            data.append(d)
        pprint.pprint(data)

        print("start write page {}/{} to xlsx {}".format(i, count, filepath))
        for d in data:
            worksheet.write(row, 0, d['datetime'])
            worksheet.write(row, 1, d['content'])
            if d.get('link'):
                worksheet.write(row, 2, d['link'])

            # get photo data
            if d.get('photo'):
                r = session.get(d['photo'])
                if r.status_code != 200:
                    print("err fetch {}: {} {}".format(d['photo'], r.reason, r.status_code))
                    continue

                # save photo
                os.makedirs(photo_dir, exist_ok=True)
                img = "{}/{}.jpg".format(photo_dir, d['datetime'])
                with open(img, "wb") as f:
                    f.write(r.content)
                
                preview = session.get(d['preview'])
                if preview.status_code != 200:
                    continue
                worksheet.insert_image(row, 3, img, {'image_data': BytesIO(preview.content)})
                worksheet.set_row(row, 100)
                worksheet.write_url(row, 4, img)
                worksheet.write(row, 5, d.get('photo'))
            row += 1
        time.sleep(0.04 + random.random() * 0.01)

    print("succeed.")

