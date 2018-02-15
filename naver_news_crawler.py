# -*- coding: utf-8 -*-
import itertools
import hashlib
import urllib.request
#import httplib2
from datetime import datetime, timedelta
from functools import singledispatch
from bs4 import BeautifulSoup, element
import news_document_class as nd
import re
import time


@singledispatch
def get_crawling_list(date_to_crawl, category_to_crawl = ["100","101","102","103","104","105"]):
    '''
    지정한 날짜와 전체 분야(정치, 사회 등)을 cross join하여 반복문을 돌릴 crawling_list를 반환한다.
    :param date_to_crawl: 크롤링할 날짜 (string)
    :param category_to_crawl: 크롤링할 분야를 원소로 갖는 리스트 (list)
    :return: crawling_list #[[ct1, dt1], [ct2, dt1], ... , [ct2, dt2] : the list of [category, datetime] to crawl
    '''
    result = [x for x in itertools.product([date_to_crawl], category_to_crawl)]
    return sorted(result, key=lambda k:k[0])


@get_crawling_list.register(datetime)
def _(date_to_crawl, category_to_crawl = ["100","101","102","103","104","105"]):
    '''
    지정한 날짜와 전체 분야(정치, 사회 등)을 cross join하여 반복문을 돌릴 crawling_list를 반환한다.
    :param date_to_crawl: 크롤링할 날짜 (datetime)
    :param category_to_crawl: 크롤링할 분야를 원소로 갖는 리스트 (list)
    :return: crawling_list #[[ct1, dt1], [ct2, dt1], ... , [ct2, dt2] : the list of [category, datetime] to crawl
    '''
    date_to_crawl = date_to_crawl.strftime("%Y-%m-%d")
    result = [x for x in itertools.product([date_to_crawl], category_to_crawl)]
    return sorted(result, key=lambda k:k[0])


@get_crawling_list.register(list)
def _(date_to_crawl, category_to_crawl = ["100","101","102","103","104","105"]):
    '''
    지정한 날짜와 전체 분야(정치, 사회 등)을 cross join하여 반복문을 돌릴 crawling_list를 반환한다.
    :param date_to_crawl: [start_date, end_date] 크롤링할 날짜의 범위를 나타내는 string을 원소로 갖는 리스트 (list)
    :param category_to_crawl: 크롤링할 분야를 원소로 갖는 리스트 (list)
    :return: crawling_list #[[ct1, dt1], [ct2, dt1], ... , [ct2, dt2] : the list of [category, datetime] to crawl
    '''
    date_to_crawl = [datetime.strptime(x, '%Y-%m-%d') for x in date_to_crawl]
    max_date = max(date_to_crawl)
    min_date = min(date_to_crawl)
    date_list = [(max_date - timedelta(days=x)).strftime("%Y-%m-%d") for x in range(0, (max_date - min_date).days+1)]
    result = [x for x in itertools.product(date_list, category_to_crawl)]
    return sorted(result, key=lambda k:k[0])


class crawler:
    def __init__(self, date_to_crawl, path="/Users/hodong/PycharmProjects/news_bot/chromedriver"):
        self.date_to_crawl = date_to_crawl
        self.date_list = get_crawling_list(date_to_crawl)
        self.error_list = []
        self.path = path


    def get_html_by_urllib(self, url):
        '''
        url을 받아서 해당 페이지의 html 코드를 반환한다.
        :param url: url 링크 (string)
        :return: html 문서 (string)
        '''
        #방법. 역시 잘안됨
        #_html = ""
        #resp = requests.get(url)
        #_html = resp.text
        #if resp.status_code == 200:
        #    _html = resp.text

        #방법2. 잘안됨
        #resp = urllib.request.Request(url)
        _html = urllib.request.urlopen(url).read()

        return _html


    def get_links_from_page(self, url):
        '''
        url을 받아서 해당 페이지에서 크롤링할 뉴스 문서들의 링크들을 리스트 형태로 반환한다. 
        :param url: url 링크 (string)
        :return: 뉴스 링크(string)들을 원소로 갖는 리스트 (list)
        '''
        page_html = self.get_html_by_urllib(url)
        page_bs = BeautifulSoup(page_html, 'html.parser')

        ul_tags = [a_tag["href"] for ul_tag in page_bs.find_all("ul", {"class": "slist1"})
                                    for a_tag in ul_tag.find_all("a")]
        dl_tags = [a_tag["href"] for dl_tag in page_bs.find_all("dl", {"class": "sphoto1"})
                                    for a_tag in dl_tag.find_all("a")]
        div_tags1 = [a_tag["href"] for div_tag in page_bs.find_all("div", {"class": "head_parallel"})
                                    for a_tag in div_tag.find_all("a")]
        div_tags2 = [a_tag["href"] for div_tag in page_bs.find_all("div", {"class": "section_body"})
                                    for a_tag in div_tag.find_all("a")]

        #with open("temp.txt", "w") as fp : fp.write(page_bs)

        link_to_crawl = ul_tags + dl_tags + div_tags1 + div_tags2
        link_to_crawl = list(set(link_to_crawl))

        link_to_crawl = [x for x in link_to_crawl if re.search("&sid1=", x) is not None]
        for i in range(0, len(link_to_crawl)) :
            if re.search("http://news.naver.com", link_to_crawl[i]) is None:
                link_to_crawl[i] = "http://news.naver.com" + link_to_crawl[i]

        return link_to_crawl


    def get_hash_from_text(self, text):
        '''
        뉴스 기사 본문을 md5로 해싱하고 10진수 int로 변환한 unique한 id를 반환한다.
        :param text: 뉴스 기사 본문 (string)
        :return: hash value (string)
        '''
        hasher = hashlib.md5()
        text = text.encode("utf-8")
        hasher.update(text)
        return str(int(hasher.hexdigest(), 16))


    def get_document_from_page(self, url) :
        '''
        url을 받아서 해당하는 뉴스 기사 정보(id/press/category/published_date/title/text/link/sentiment_list)를 모두 담은 nd.Document 객체를 반환한다.
        :param url: url 링크 (string)
        :return: 뉴스 기사 정보를 모두 담은 nd.Document 객체 (nd.Document)
        '''
        category_dict = {"100": "정치", "101": "경제", "102": "사회", "103": "생활/문화", "104": "세계", "105": "IT/과학"}
        page_html = self.get_html_by_urllib(url)
        page_bs = BeautifulSoup(page_html, 'html.parser')
        press = page_bs.find("div", {"class": "press_logo"}).find("img")["title"]
        category = category_dict[url[(url.index("sid1=") + len("sid1=")):(url.index("sid1=") + len("sid1=") + 3)]]
        published_date = page_bs.find("div", {"class": "sponsor"}).find("span", {"class": "t11"}).text
        title = page_bs.find("div", {"class": "article_info"}).find("h3", {"id": "articleTitle"}).text.strip()

        try :
            good = page_bs.find("li", {"class": ["u_likeit_list", "good"]}).find("span", {"class": "u_likeit_list_count"}).text
            warm = page_bs.find("li", {"class": ["u_likeit_list", "warm"]}).find("span", {"class": "u_likeit_list_count"}).text
            sad = page_bs.find("li", {"class": ["u_likeit_list", "sad"]}).find("span", {"class": "u_likeit_list_count"}).text
            angry = page_bs.find("li", {"class": ["u_likeit_list", "angry"]}).find("span",{"class": "u_likeit_list_count"}).text
            want = page_bs.find("li", {"class": ["u_likeit_list", "want"]}).find("span", {"class": "u_likeit_list_count"}).text
            sentiment_list = [good, warm, sad, angry, want]
            content = page_bs.find("div", {"id": "articleBodyContents"}).text
            pattern = "// flash 오류를 우회하기 위한 함수 추가\nfunction _flash_removeCallback() {}"
            text = content.replace(pattern, "").strip()
            document_id = self.get_hash_from_text(text)
        except Exception as e :
            return None #내용이 빠진 뉴스기사일 경우 뛰어넘는다.

        if len(text) <= 30 : return None
        news = nd.Document(document_id=document_id, press=press, category=category, published_date=published_date,
                        title=title, text=text, link=url, sentiment_list=sentiment_list)

        return news


    def crawl_from_datelist_element(self, date_list_element) :
        '''
        하나의 date_list 원소(크롤링하고자 하는 날짜와 카테고리로 이루어진 tuple)에 해당하는 모든 페이지의 링크를 수집하고 
        각 링크에서 수집한 뉴스기사, 뉴스 기사를 전처리한 결과물, 그리고 각 뉴스 기사에 대한 댓글 정보를 각각 리스트의 형태로 반환한다.  
        :param date_list_element: (datetime, category)의 형태 (tuple)
        :return1: nd.Document class 객체를 원소로 갖는 리스트 (list)
        :return2: nd.Document_summary class 객체를 원소로 갖는 리스트 (list)
        :return3: nd.Comment class 객체를 원소로 갖는 리스트 (list)
        '''
        page_url = "http://news.naver.com/main/main.nhn?mode=LSD&mid=shm&sid1=" + date_list_element[1] + "#&date=" + date_list_element[0] + "+00:00:00&page="

        target_links = []
        for page in range(1,31) :

            len_before_update = len(target_links)
            url = page_url + str(page)
            temp_links = self.get_links_from_page(url)
            target_links = target_links + temp_links
            target_links = list(set(target_links))
            len_after_update = len(target_links)
            if len_before_update==len_after_update : break

        nd_document_list = []
        nd_document_summary_list = []

        #target_links = target_links[0:5] #테스트용
        for target_link in target_links :
            doc = self.get_document_from_page(target_link)
            if doc==None : continue

            doc_summary = nd.Document_summary(doc)
            nd_document_list.append(doc)
            nd_document_summary_list.append(doc_summary)
            #if len(nd_document_list)==10 : break #테스트용

        return nd_document_list, nd_document_summary_list


    def naver_news_crawl(self) :
        '''
        주어진 날짜 기간에 해당하는 모든 네이버 뉴스를 크롤링하여 mini batch로 반환한다. 
        parameter인 date_list에서 1개의 원소를 pop()하여 처리하고 결과값을 반환하며 오류 발생시 error_list에 삽입하여 반환한다.
        DB에 저장하는 장고 코드와 while문을 이용해 mini batch를 구현한다.
        :param date_list: crawling_list #[[ct1, dt1], [ct2, dt1], ... , [ct2, dt2] : the list of [category, datetime] to crawl
        :return1: nd_list = nd.Document class 객체를 원소로 갖는 리스트 (list)
        :return2: comment_dict = nd.id를 key로, nd.comment class 변수를 value로 갖는 사전 (dictionary)
        :return3: pop()하여 크롤링하고 남은 date_list 대상 (list)
        :return4: error_list (크롤링에 실패하면 date_list 원소로 이루어진 리스트) (list)
        '''
        date_list_element = (self.date_list).pop()
        try :
            nd_list, nd_summary_list= self.crawl_from_datelist_element(date_list_element)
        except Exception as e :
            (self.error_list).insert(0, date_list_element)
            print(e)
        else :
            return nd_list, nd_summary_list