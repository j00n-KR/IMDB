#-*- coding: utf-8 -*-
import pandas as pd
import selenium 
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import requests
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
import time
import urllib.request
from selenium.webdriver.common.keys import Keys
import warnings
import datetime

# PATH 설정
PATH = r"D:\Big Data\chromedriver.exe"

warnings.filterwarnings(action='ignore')

def get_review(url,folder_name,no,no_):

    # 경과 시간 확인을 위한 설정
    start = time.time()

    # 시간 확인용 현재 시간 설정
    now = datetime.datetime.now()
    nowDatetime = now.strftime('%Y-%m-%d %H:%M:%S')

    # SELENIUM
    options = webdriver.ChromeOptions()
    options.add_argument("headless")
    driver = webdriver.Chrome(PATH, options=options)
    driver.get(url)
    driver.implicitly_wait(1)
    

    # LOGIN / 한국어로 나오는 제목 존재
    driver.find_element_by_css_selector("div.ipc-page-content-container.ipc-page-content-container--center.navbar__inner > div._3x17Igk9XRXcaKrcG3_MXQ.navbar__user.UserMenu-sc-1poz515-0.eIWOUD > a").click()
    driver.find_element_by_class_name("auth-provider-text").click()
    driver.find_element_by_id('ap_email').send_keys('hwangjoon0@naver.com')
    driver.find_element_by_id('ap_password').send_keys('ghkdwns0')
    driver.find_element_by_css_selector("div:nth-child(2) > div > div > form > div > div > div > div.a-section.a-spacing-extra-large > div > div > label > div > label > input[type=checkbox]").click()
    driver.find_element_by_id('signInSubmit').click()
    driver.execute_script('window.open("about:blank", "_blank");')
    driver.get(url)
    driver.switch_to.window((driver.window_handles[0]))

    # 이미지 로딩을 위한 위아래 스크롤
    for i in range(0,30):
        try:
            driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_DOWN)
        except:
            continue

    for i in range(0,30):
        try:
            driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_UP)
        except:
            continue
    

    # 정보 저장을 위한 list
    NO = []
    title = []
    titles = []
    link = []
    year = []
    genre = []
    rate = []
    votes = []
    directors = []
    stars = []
    story = []
    gross = []
    url = []
    certificate = []


    # 영화 한편을 단위로 설정
    block = driver.find_elements_by_class_name('lister-item')

    for i in range(0,50):

        ftitle = block[i].find_element_by_class_name('lister-item-header').text

        # 순서
        try:
            forder = block[i].find_element_by_class_name('lister-item-index').text
        except:
            forder = "NA"

        # 연도
        try:
            fyear = ftitle[-6:]
            #Drop the order, year and only keep the movie's name
        except:
            fyear = "NA"

        # 제목
        try:
            ftitles = block[i].find_element_by_css_selector('h3 > a').text
            try:
                ftitles = ftitles.replace(":"," -")
                ftitles = ftitles.replace("?","")
                ftitles = ftitles.replace("/","-")
            except:
                continue
        except:
            ftitles = "NA"

        # 리뷰 링크
        try:
            #Then extract the link with cleaned title
            flink = block[i].find_element_by_css_selector('h3 > a').get_attribute('href')
        except:
            flink = "NA"

        # 장르
        try:
            fgenre = block[i].find_element_by_class_name('genre').text
        except:
            fgenre = "NA"

        # 평점    
        try:
            frates = block[i].find_element_by_css_selector('.ratings-imdb-rating').find_element_by_tag_name('strong').text
        except:
            frates = "NA"

        # 투표 수
        try:
            fvotes = block[i].find_elements_by_name('nv')[0].get_attribute('data-value')
        except:
            fvotes = "NA"

        # 감독 및 배우
        try:
            f_info = block[i].find_element_by_css_selector('p:nth-child(5)').text
            f_info_1 = f_info.split("|")
            fdirectors = f_info_1[0].replace("Director: ","")
            fstars = f_info_1[1].replace(" Stars: ","")
        except:
            fdirectors = "NA"
            fstars = "NA"

        # 줄거리
        try:
            fstory = block[i].find_element_by_css_selector('p:nth-child(4)').text
        except:
            fstory = "NA"

        # 연령 제한
        try:
            fcertificate = block[i].find_element_by_class_name("certificate").text
        except:
            fcertificate = "NA"

        # 매출
        try:
            fgross = block[i].find_element_by_css_selector('p.sort-num_votes-visible > span:nth-child(5)').text
        except:
            fgross = "NA"

        # 포스터/이미지
        try:
            fimage = block[i].find_element_by_class_name("loadlate")
            url.append(fimage.get_attribute("src"))
        except:
            continue    
        
        NO.append(no)
        no +=1
        title.append(ftitles)
        titles.append(str(ftitles))
        year.append(fyear)
        link.append(flink)

        genre.append([fgenre])
        rate.append(frates)
        votes.append(fvotes)
        directors.append([fdirectors])
        stars.append([fstars])
        story.append([fstory])
        gross.append(fgross)
        certificate.append(fcertificate)
    
    print("\n",len(NO)," Movies LOADED")
    print(nowDatetime)

    # 포스터/이미지 저장
    for i in range(len(url)):
        urllib.request.urlretrieve(url[i], f'D:/Big Data/IMDB/{folder_name}/'+ str(NO[i])+ "." + title[i] + '.jpeg')

    # 경과 시간 알리기 용
    print("movie_info COMPLETE : ",round((time.time() - start)/60,3),"MIN\n")

    # 리뷰 링크
    user_review_links = []
    for url in link:
        review_link = url.replace("?ref_=adv_li_tt","reviews?ref_=tt_urv")
        user_review_links.append(review_link)

    # DataFrame 생성
    top_data = {'Movie_name': title, 
            'Year': year, 
            'link': link,
            'user_review' : user_review_links,
            }
    top = pd.DataFrame(data = top_data) #create dataframe
    driver.quit() #tell Selenium to close the webpage

    # DataFrame 생성
    movie_inf = {'NO' : NO,
        'Movie_title': titles, 
        'Year': year,
        'Genre': genre,
        'Rating' : rate,
        'Votes' : votes,
        'Directors' : directors,
        'Stars' : stars,
        'Scenario' : story,
        'Gross' : gross,
        'Certificate' : certificate
        }

    movie_info = pd.DataFrame(data = movie_inf)
    movie_info.to_csv(f'D:/Big Data/IMDB/{folder_name}/movie_info.csv',encoding='utf-8-sig')
    

    # 유저 리뷰 가져오기
    for i in range(len(top['user_review'])):
        options = webdriver.ChromeOptions()
        options.add_argument("headless")
        options.add_argument('window-size=1920x1080')
        options.add_argument("disable-gpu") 
        driver = webdriver.Chrome(PATH, options=options)
        driver.get(top['user_review'][i])
        driver.implicitly_wait(1)


        # LOAD MORE 를 위한 설정
        page = 1
        while page < 10000:  
            try:
                load_more = driver.find_element_by_id('load-more-trigger')
                load_more.click()
                page+=1
                driver.implicitly_wait(3)
            except:
                print("\n",page," pages LOAD COMPLETE : ",round((time.time() - start)/60,3),"MIN\n")
                break
        
        review = driver.find_elements_by_class_name('review-container')
        title = []
        content = []
        rating = []
        date = []
        user_name = []
        for n in range(0,100000):
            try:
                ftitle = review[n].find_element_by_class_name('title').text
                try:
                    fcontent = review[n].find_element_by_class_name('text.show-more__control').get_attribute("textContent").strip()
                except:
                    fcontent = ftile
                frating = review[n].find_element_by_css_selector('div.lister-item-content > div.ipl-ratings-bar > span > span:nth-child(2)').text
                fdate = review[n].find_element_by_class_name('review-date').text
                fname = review[n].find_element_by_class_name('display-name-link').text

                title.append(ftitle)
                content.append(fcontent)
                rating.append(frating)
                date.append(fdate)
                user_name.append(fname)
                print(no_,":",top['Movie_name'][i],"'s ",n+1," REVIEWS LOADED ",round((time.time() - start)/60,3),"MIN")
            except:
                continue

        data = {'User_name': user_name, 
            'Review title': title, 
            'Review Rating': rating,
            'Review date' : date,
            'Review_body' : content
           }
           
        print("\n",no_,":",top['Movie_name'][i], "review LOAD COMPLETED",n+1,round((time.time() - start)/60,3),"MIN\n")
        print(nowDatetime)

        review = pd.DataFrame(data = data)
        movie = top['Movie_name'][i] 
        review['Movie_name'] = movie
        review.to_csv(f'D:/Big Data/IMDB/{folder_name}/{no_}.{movie}.csv',encoding='utf-8-sig')
        no_+=1
        driver.quit()

# 실행
for i in range(1,2951,50):
    IMDB = 'https://www.imdb.com/search/title/?title_type=feature&user_rating=1.0,10.0&num_votes=10000,&count=50&start='+str(i)
    get_review(IMDB, ('IMDB_FROM_'+str(i)+'_to_'+str(i+49)),int(i),int(i))