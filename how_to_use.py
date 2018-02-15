# -*- coding: utf-8 -*-
import news_document_class as nd
import text_rank as tr
import naver_news_crawler as cr


crawler = cr.crawler("2018-01-06")
crawler.date_list.pop()
crawler.date_list.pop()
crawler.date_list.pop()

print("before :\n", crawler.date_list, "\n", crawler.error_list)
nd_doc_list, nd_summary_list = crawler.naver_news_crawl()
print("after :\n", crawler.date_list, "\n", crawler.error_list)
print("nd_doc len :", len(nd_doc_list), "\tnd_summary len :", len(nd_summary_list))

print("\n\nDocument : ")
nd_doc_list[0].print_document()
print("\n\nDocument_summary : ")
nd_summary_list[0].print_document_summary()

for i in range(0,5) :
    with open(("sample_news/news"+str(i)+".txt"), mode="w") as fp:
        fp.write(nd_doc_list[i].text)
