from selenium import webdriver as wd
from bs4 import BeautifulSoup
import time
cService = wd.ChromeService(executable_path='C:/Users/cdtt3/AppData/Local/Programs/Python/Python312/chromedriver/chromedriver.exe')
browser = wd.Chrome(service = cService)
browser.get("https://sudrf.ru/index.php?id=300&act=go_search&searchtype=fs&court_name=%F1%F3%E4&court_subj=0&court_type=0&court_okrug=0&vcourt_okrug=0")
print("time start")
##time.sleep(30)
print("time stop")
soup = BeautifulSoup(browser.page_source, 'html')
all_li=soup.find_all("ul", {"class":"search-results"})[0].find_all("li")
names=""
for i in all_li:
        names+=i.find("a").text+'\n'
with open("court_names.txt", "w") as file:
    file.write(names)
    

