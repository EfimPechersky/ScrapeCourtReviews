
from selenium import webdriver as wd
from bs4 import BeautifulSoup
import time
cService = wd.ChromeService(executable_path='C:/Users/EfimPechersky/AppData/Local/Programs/Python/Python312/chromedriver-win64/chromedriver.exe')
browser = wd.Chrome(service = cService)
browser.get("https://arbitr.ru/")
print("time start")
##time.sleep(30)
print("time stop")
soup = BeautifulSoup(browser.page_source, 'html')
all_a=soup\
        .find("div", {"class":"popup popup-fas"})\
        .find("div", {"class":"popup__inner"})\
        .find("div", {"class":"popup__box"})\
        .find("div", {"class":"popup__content"})\
        .find("div", {"class":"search-result"})\
        .find_all("a")
names=""
for a in all_a:
    names+=a.text+'\n'
print(len(all_a))
with open("as_names.txt", "w") as file:
    file.write(names)
