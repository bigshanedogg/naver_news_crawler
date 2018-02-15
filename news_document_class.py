# -*- coding: utf-8 -*-
from konlpy.tag import Kkma
from datetime import datetime, date, time
import text_rank as tr

'''
뉴스 기사 정보를 저장할 class인 document와 document에 대한 감정 반응 정보를 담는 class 변수인 sentiment class 선언
긁은 문장에서 \n을 제거하고, "."을 더한 다시 합치는 메소드인 prettify_sentences(text) 선언
'''

def prettify_sentences(text):
    '''
    뉴스기사의 각 문장에서 "\n"을 제거하고 문장 끝에 "."을 추가한 뒤 합친 string으로 반환한다.
    :param text: 뉴스기사 텍스트 (string) or 뉴스기사의 문장들을 원소로 갖는 리스트 (list)
    :return: 정돈된 뉴스기사 텍스트 (string)
    '''
    # document = kkma.sentences(doc) #문서를 문장 단위로 나눔. 그러나 원하지 않는 부분(eg. 종속절&주절)이 분리되기도 한다.
    if type(text) == str:
        text = text.split(".")  # 구조화된 뉴스 데이터는 "."으로 나누는 게 더 유의미할 듯하다.

    sentences = []
    for sentence in text:
        sentence = sentence.replace("\n", "").strip() + "."
        sentences.append(sentence)

    return " ".join(sentences)


class Sentiment:
    '''
    document에 대한 감정평가(good, warm, sad, angry, want) 정보를 저장할 class
    '''
    def __init__(self, sentiment_list):
        self.good = sentiment_list[0]
        self.warm = sentiment_list[1]
        self.sad = sentiment_list[2]
        self.angry = sentiment_list[3]
        self.want = sentiment_list[4]

    def print_sentiment(self):
        '''
        sentiment 정보를 출력하는 메소드
        :return: None
        '''
        print("good :", self.good, "\twarm :", self.warm,
              "\tsad :", self.sad, "\tangry :", self.angry, "\twant :", self.want)


class Document:
    '''
    뉴스 문서의 id, 신문사, 분류, 업로드 날짜, 크롤링한 날짜, 제목, 기사 본문, 감정 반응 정보를 담는 class
    '''
    def __init__(self, document_id, press, category, published_date, title, text, link, sentiment_list):
        self.document_id = document_id
        self.press = press
        self.category = category
        self.published_date = datetime.strptime(published_date, '%Y-%m-%d %H:%M')
        self.crawled_date = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.title = title
        self.text = prettify_sentences(text)
        self.link = link
        self.sentiment = Sentiment(sentiment_list)

    def print_document(self):
        '''
        document 정보를 출력하는 메소드 
        :return: None
        '''
        print("document_id :", self.document_id)
        print("press :", self.press)
        print("category :", self.category)
        print("published_date :", self.published_date)
        print("crawled_date :", self.crawled_date)
        print("title :", self.title)
        print("text :", self.text)
        print("link :", self.link)
        print("sentiment_list :\n\t", end="")
        self.sentiment.print_sentiment()

    def get_news_summary(self):
        '''
        n줄 요약된 내용 출력
        :return:  상위 n개의 문장으로 이루어진 리스트 (list)
        '''
        temp = tr.text_rank(self.text)
        summary = temp.get_summary()
        return summary


class Document_summary:
    '''
    한 번 처리한 정보에 대한 처리 비용과 시간을 줄이기 위해 뉴스 문서를 전처리한 데이터를 저장하는 class
    각 문장의 text rank 값을 문장의 index순으로 나열한 list 형태로, 
    상위 100개의 단어와 그 count, tfidf 값을 각각 key/value로 갖는 dictionary 형태로 저장한다. 
    '''
    def __init__(self, document):
        self.document_id = document.document_id
        self.sentences_n = len((document.text).split("."))

        temp = tr.text_rank(document.text)
        temp.select_summary_n()

        self.text_rank = temp.get_textrank_from_text()

        word_count = dict()
        count_feature, count_vec = temp.get_count_vector()
        for x, y in zip(count_feature, count_vec):
            word_count[x] = y
        self.word_count = word_count

        word_tfidf = dict()
        tfidf_feature, tfidf_vec = temp.get_tfidf_vector()
        for x, y in zip(tfidf_feature, tfidf_vec):
            word_tfidf[x] = y
        self.word_tfidf = word_tfidf
        self.summary_text = temp.get_summary()

    def print_document_summary(self):
        '''
        전처리된 뉴스 문서의 정보를 출력하는 메소드
        :return: None
        '''
        print("document_id :", self.document_id)
        print("sentences_n :", self.sentences_n)
        print("text_rank :", self.text_rank)
        print("word_count :", self.word_count)
        print("word_tfidf :", self.word_tfidf)
        print("summary_text :", self.summary_text)


class Comment:
    '''
    뉴스 문서 댓글의 할당된 뉴스 기사 id, 댓글 자체의 id, 댓글 내용, 업로드 날짜, 크롤링한 날짜, 추천수, 비추천수를 담는 class
    '''
    def __init__(self, user_id, content, published_date, recomm, unrecomm):
        self.document_id = None
        self.user_id = user_id
        self.content = content
        self.published_date = datetime.strptime(published_date, '%Y-%m-%d %H:%M:%S')
        self.crawled_date = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.recomm = recomm
        self.unrecomm = unrecomm

    def update_document_id(self, document_id):
        '''
        먼저 해당 페이지의 댓글을 크롤링하고 이후에 news document와 key로 연결하기 때문에 class 객체 생성 후 업데이트한다.
        :param document_id: 연결되는 뉴스 문서의 document_id (1:N 관계에서 부모 객체의 PK) (string)
        :return: None
        '''
        self.document_id = document_id

    def print_comment(self):
        '''
        comment 정보를 출력하는 메소드 
        :return: None
        '''
        print("document_id :", self.document_id)
        print("user_id :", self.user_id)
        print("content :", self.content)
        print("published_date :", self.published_date)
        print("crawled_date :", self.crawled_date)
        print("recomm :", self.recomm)
        print("unrecomm :", self.unrecomm)