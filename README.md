# Naver News Crawler<br>
<br>
## naver\_news\_crawler.py
"naver\_news\_crawler.py" is a code for fetching articles from Naver News, a Korean portal site. It crawls news document including press, category, content, publised date and crawling date, and create unique key by hashing document content using BeautifulSoup4. It is the limitation that it can only crawl the html floated on naver news page not that of specific date.<br>
<br>
## naver\_news_crawler\_w\_comment.py
"naver\_news_crawler\_w\_comment.py" is revised version of "naver\_news\_crawler.py" in that specific datetime range can be set and also comments of each news article can be collected using Selenium. (It priorly needs web driver such as Chrome) but, It has a limitation that it doesn't work well on AWS, which means It is not appropriate for continuous and stable information supply and demand.<br>

News articles crawled by both codes are saved as Document class and Comment class defined in "news\_document\_class.py", So It should be imported before crawling.<br>
<br>
<hr>
## How to use
#### 1) Import modules
<pre><code>import news\_document\_class as nd
import naver\_news\_crawler as cr<br></code></pre>

#### 2) Creat Crawler object
"2018-01-06 is date to crawl, it doesn't work on "naver\_news\_crawler.py"
<pre><code>crawler = cr.crawler("2018-01-06")
\#print("before :\n", crawler.date\_list, "\n", crawler.error\_list)
nd\_doc\_list, nd\_summary\_list = crawler.naver\_news\_crawl()
\#print("after :\n", crawler.date_list, "\n", crawler.error\_list)
\#print("nd\_doc len :", len(nd\_doc\_list), "\tnd\_summary len :", len(nd\_summary\_list))
</code></pre>

("error_list" is a list that stores the error category and date information when an error occurs during crawling. )

#### 3) Save crawled news articles
<pre><code>for i in range(0,len(nd_doc_list)) :
	with open(("sample_news/news"+str(i)+".txt"), mode="w") as fp:
          fp.write(nd_doc_list[i].text)
</code></pre>

(check crawled article with below code)
<pre><code>print("\nDocument : ")
nd\_doc\_list[0].print\_document()
print("\nDocument\_summary : ")
nd\_summary\_list[0].print\_document\_summary()
</code></pre>


<hr>
This code has been written in 2018 JAN, and works well in 2018 FEB. (but, Crawling is dependent on external condition, not sure when it be blocked.)
