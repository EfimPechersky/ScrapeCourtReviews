from selenium import webdriver as wd
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
import json
import time
cService = wd.ChromeService(executable_path='C:/Users/cdtt3/AppData/Local/Programs/Python/Python312/chromedriver/chromedriver.exe')
browser = wd.Chrome(service = cService)
browser.get("https://www.google.com/maps/")
start=int(input())
end=int(input())
def get_reviews(browser, name):
    search_box = browser.find_element(By.XPATH,'//input[contains(@class, "xiQnY")]')
    search_box.send_keys(name)
    browser.find_element(By.XPATH,'//button[contains(@class, "mL3xi")]').click()
    time.sleep(3)
    soup = BeautifulSoup(browser.page_source, 'html')
    place_name = soup.find("h1",{"class","DUwDvf lfPIob"})
    place_type = soup.find("button",{"class","DkEaL"})
    if place_name!=None and place_type!=None:
        place_name=place_name.text
        place_type=place_type.text
    try:
        browser.find_element(By.XPATH,'//button[contains(@aria-label, "Отзывы о месте")]').click()
    except NoSuchElementException:
        try:
            browser.find_element(By.XPATH,'//div[contains(@class, "Nv2PK Q2HXcd THOPZb")]').click()
            time.sleep(3)
            soup = BeautifulSoup(browser.page_source, 'html')
            place_name = soup.find("h1",{"class","DUwDvf lfPIob"})
            place_type = soup.find("button",{"class","DkEaL"})
            if place_name!=None and place_type!=None:
                place_name=place_name.text
                place_type=place_type.text
            browser.find_element(By.XPATH,'//button[contains(@aria-label, "Отзывы о месте")]').click()
        except:
            search_box.clear()
            return None
    if place_type==None:
        return None
    time.sleep(3)
    soup = BeautifulSoup(browser.page_source, 'html')
    review_count=soup.find("div", {"class", "jANrlb"}).find("div", {"class","fontBodySmall"})
    if review_count!=None:
        if review_count.text.split(" ")[1]!="отзыв":
            if int(review_count.text.split(" ")[1])>10:
                reviews_container = browser.find_element(By.XPATH, '//div[contains(@class, "m6QErb DxyBCb kA9KIf dS8AEf XiKgde")]')
                last_height=reviews_container.size['height']
                new_height=last_height
                while True:
                    browser.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight-1000", reviews_container)
                    time.sleep(1)
                    reviews_container = browser.find_element(By.XPATH, '//div[contains(@class, "m6QErb DxyBCb kA9KIf dS8AEf XiKgde")]')
                    last_height=new_height
                    new_height=reviews_container.size['height']
                    if new_height==last_height:
                        break
    soup = BeautifulSoup(browser.page_source, 'html')
    all_reviews = soup.find_all("div",{"class":"jJc9Ad"})
    reviews=[]
    review={}
    for r in all_reviews:
        name=r.find("div", {"class":"d4r55"}).text
        try:
            rating=int(r.find("span", {"class":"kvMYJc"})["aria-label"][0])
        except:
            rating=0
        date=r.find("span",{"class":"rsqaWe"}).text
        try:
            text=r.find("span",{"class":"wiI7pd"}).text
        except:
            text=""
        try:
            likes=int(r.find("span",{"class":"pkWtMe"}).text)
        except:
            likes=0
        review={"name":name,
                "rating":rating,
                "date":date,
                "text":text,
                "likes":likes
                }
        reviews+=[review]
    search_box.clear()
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
with open("google_as_data"+str(start)+str(end)+".json","w") as file:
    json.dump(all_courts,file)

#nametest=input()
#review1=get_reviews(browser,nametest)
#print(review1)
    
        
