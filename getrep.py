from selenium import webdriver as wd
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
import json
import time
cService = wd.ChromeService(executable_path='C:/Users/cdtt3/AppData/Local/Programs/Python/Python312/chromedriver/chromedriver.exe')
browser = wd.Chrome(service = cService)
browser.get("https://yandex.ru/maps/")
start=int(input())
end=int(input())
def get_reviews(browser, name):
    search_box = browser.find_element(By.XPATH,'//input[contains(@placeholder, "Поиск и выбор мест")]')
    search_box.send_keys(name)
    browser.find_element(By.XPATH,'//button[contains(@class, "button _view_search _size_medium")]').click()
    close_button=browser.find_element(By.XPATH,'//button[contains(@aria-label, "Закрыть")]')
    time.sleep(3)
    try:
        browser.find_element(By.XPATH,'//div[contains(@class, "_name_reviews")]').click()
    except NoSuchElementException:
        try:
            browser.find_element(By.XPATH,'//div[contains(@class, "search-business-snippet-view")]').click()
            time.sleep(3)
            browser.find_element(By.XPATH,'//div[contains(@class, "_name_reviews")]').click()
        except:
            close_button.click()
            return None
    time.sleep(3)
    soup = BeautifulSoup(browser.page_source, 'html')
    place_name=soup.find("h1",{"class","card-title-view__title"}).text
    if "суд" not in place_name.lower():
        print("not court")
        close_button.click()
        return None
    review_count=soup.find("div", {"class", "tabs-select-view__title _name_reviews _selected"}).find("div", {"class","tabs-select-view__counter"})
    if review_count!=None:
        if int(review_count.text)>50:
            reviews_container = browser.find_element(By.XPATH, '//div[contains(@class, "scroll__container")]')
            while True:
                # Прокручиваем внутри контейнера вниз на его высоту
                browser.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight-1000", reviews_container)
                time.sleep(1)  # подождите, чтобы отзывы прогрузились
                try:
                    browser.find_element(By.XPATH, '//div[contains(@aria-posinset, "600")]')
                    break
                except:
                    try:
                        browser.find_element(By.XPATH, '//div[contains(@aria-posinset, "'+review_count.text+'")]')
                        break  # достигли конца отзывов
                    except:
                        continue
    soup = BeautifulSoup(browser.page_source, 'html')
    all_reviews = soup.find_all("div",{"class":"business-review-view__info"})
    reviews=[]
    review={}
    for r in all_reviews:
        name=r.find("div",{"class":"business-review-view__author-name"}).find("span").text
        try:
            rating=r.find("meta", {"itemprop":"ratingValue"})["content"]
        except:
            rating=0
        try:
            date=r.find("span",{"class":"business-review-view__date"}).find("meta", {"itemprop":"datePublished"})["content"]
        except:
            date=r.find("span",{"class":"business-review-view__date"}).find("span").text
        text=r.find("div",{"class":"business-review-view__body"}).find("span", {"class":"business-review-view__body-text"}).text
        likes_counter=r.find("div",{"aria-label":"Лайк"}).find("div",{"class":"business-reactions-view__counter"})
        likes=0
        if likes_counter!=None:
            likes=likes_counter.text
        dislikes_counter=r.find("div",{"aria-label":"Дизлайк"}).find("div",{"class":"business-reactions-view__counter"})
        dislikes=0
        if dislikes_counter!=None:
            dislikes=dislikes_counter.text
        review={"name":name,
                "rating":rating,
                "date":date,
                "text":text,
                "likes":likes,
                "dislikes":dislikes
                }
        reviews+=[review]
    close_button.click()
    return place_name,reviews
all_courts={}
with open("as_names.txt") as file:
    names=file.read().split("\n")
    count=0
    for i in names[start:end]:
        count+=1
        res=get_reviews(browser,i)
        if res!=None:
            place_name,reviews=res
            all_courts[place_name]=reviews
        print(count+start-1)
with open("as_data"+str(start)+str(end)+".json","w") as file:
    json.dump(all_courts,file)

#nametest=input()
#review1=get_reviews(browser,nametest)
#print(review1)
    
        
