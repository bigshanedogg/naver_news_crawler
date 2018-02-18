# Naver News Crawler<br>
<br>

## naver_news_crawler.py
"naver_news_crawler.py" is the code for fetching articles from Naver News, a Korean portal site. It crawls news document including press, category, content, publised date and crawling date, and create unique key by hashing document content using BeautifulSoup4. It is the limitation that it can only crawl the html floated on naver news page not that of specific date.<br>
<br>

## naver_news_crawler_w_comment.py
"naver_news_crawler_w_comment.py" is revised version of "naver_news_crawler.py" in that specific datetime range can be set and also comments of each news article can be collected using Selenium. (It priorly needs web driver such as Chrome) but, It has a limitation that it doesn't work well on AWS, which means It is not appropriate for continuous and stable information supply and demand.<br>
<br>
News articles crawled by both codes are saved as Document class and Comment class defined in "news_document_class.py", So It should be imported before crawling.<br>
<hr>
<br>

## How to use
#### 1) Import modules
<pre><code>import news_document_class as nd
import naver_news_crawler as cr<br></code></pre>

#### 2) Creat Crawler object
"2018-01-06 is date to crawl, it doesn't work on "naver_news_crawler.py"
<pre><code>crawler = cr.crawler("2018-01-06")
\#print("before :\n", crawler.date_list, "\n", crawler.error_list)
nd_doc_list, nd_summary_list = crawler.naver_news_crawl()
\#print("after :\n", crawler.date_list, "\n", crawler.error_list)
\#print("nd_doc len :", len(nd_doc_list), "\tnd_summary len :", len(nd_summary_list))
</code></pre>

("error_list" is a list that stores the error category and date information when an error occurs during crawling. )

#### 3) Save crawled news articles
<pre><code>for i in range(0,len(nd_doc_list)) :
	with open(("sample_news"+str(i)+".txt"), mode="w") as fp:
          fp.write(nd_doc_list[i].text)
</code></pre>

(check crawled article with below code)
<pre><code>print("\nDocument : ")
nd_doc_list[0].print_document()
print("\nDocument_summary : ")
nd_summary_list[0].print_document_summary()
</code></pre>


<hr>
This code has been written in 2018 JAN, and works well in 2018 FEB. (but, Crawling is dependent on external condition, not sure when it be blocked.)
