from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import os
import json
import re
import shutil
import requests
from bs4 import BeautifulSoup


class BookDown:
    

    def __init__(self):
    
        self.chrome_driver_path = "/Users/alikorkmaz/Dropbox/Python Works/selenium/chromedriver"
        self.browserProfile = webdriver.ChromeOptions()
        self.browser = webdriver.Chrome(self.chrome_driver_path, options=self.browserProfile)
        self.links = []
        self.my_dict = {}
        self.down = {}
        
    def getInfo(self, user, new_dir, new_dir_l, text):
        '''prefs = {"download.default_directory": new_dir,
                "download.prompt_for_download": False,
                "download.directory_upgrade": True}
        self.browserProfile.add_experimental_option("prefs", prefs)
        self.browser = webdriver.Chrome(self.chrome_driver_path, options=self.browserProfile)'''
        try:    
            self.browser.get(user)
            time.sleep(2)
            a = self.browser.find_element_by_class_name("object-view-top-block__heading-content").text
            try:
                down = self.browser.find_element_by_xpath("/html/body/div[5]/div[1]/div/div[3]/header/div/section/ul/li[3]/button")
                down.click()
                self.browser.find_element_by_xpath("/html/body/div[5]/div[1]/div/div[3]/header/div/section/ul/li[3]/div/ul/li[2]/a").click()
                print(f"{i} indirildi!")
                time.sleep(1)
                self.moveBooks(new_dir, text)
            except:
                print(f"{i} kilitli!")
                try:
                    shutil.move(new_dir, new_dir_l)
                except:
                    pass
                '''shutil.rmtree(new_dir)'''         
        except:
            print('hata')
            time.sleep(2)
            self.getInfo(user, new_dir, new_dir_l, text)
            
    def getLinks(self, user, id):
        self.browser.get(user)
        time.sleep(2)
        try:
            model = self.browser.find_element_by_class_name("searchresults").find_element_by_tag_name("ul")
            lis = model.find_elements_by_tag_name('li')
            count = len(lis)
            for li in lis:
                link = li.find_element_by_class_name("metadata").find_element_by_tag_name("a").get_attribute("href")
                self.links.append(link)
            print(f"{i}: \n sayfasından {count} adet link alındı.")
            self.saveToFile(self.links)
        except:
            print('hata')
            self.getLinks(user, id)
        
        
        
    def saveToFile(self, links):
        with open('books.txt', 'a', encoding='UTF-8') as file:
            for link in links:
                file.write(link + '\n')
        self.links = []
        
    def moveBooks(self, new_dir, text):
        source = '/Users/alikorkmaz/Downloads/' + text
        dest = new_dir + '/' + text
        try:
            shutil.move(source, dest)
            print(f"{i} taşındı!")
        except:
            time.sleep(1)
            self.moveBooks(new_dir, text)
            
    
    def close(self):
        self.browser.quit()

book = BookDown()

'''for i in range(8692,16478):
    link = f'https://www.delpher.nl/nl/boeken/results?query=&page={i}&maxperpage=10&coll=boeken'
    book.getLinks(link, i)
'''
i = 1
with open('books.txt') as file:
    lines = file.readlines()
my_dict = {}
for line in lines:
    text = re.findall(r"(?<=identifier=)(.*?)(?=&)", line)[0].replace(":", "_") + ".txt"
    line = line.replace("\n","")
    page = requests.get(line)
    soup = BeautifulSoup(page.text, 'html.parser')
    info = soup.title.text.split("»")
    book_name = info[0]
    author = info[1]
    year = soup.find_all('li', class_="view-subtitle object-view-top-block__metadata-subtitle object-view-top-block__metadata-subtitle--date")[0].text
    try:
        year = re.findall(r'\d+', year)[0]
    except:
        year = 'noinfo'
    folder = year + '_' + book_name.replace(" ", "_")[:240]
    new_dir = "/Users/alikorkmaz/Dropbox/Python Works/Books/Delpher/Delpher_Books/" + folder
    new_dir_l = "/Users/alikorkmaz/Dropbox/Python Works/Books/Delpher/Locks/" + folder
    if not os.path.exists(new_dir):
        os.makedirs(new_dir)
    my_dict["Link"] = line
    my_dict["Book Name"] = book_name
    my_dict["Author"] = author
    my_dict["Year"] = year
    with open(f'{new_dir}/info.jsonl', encoding="utf-8", mode='w') as file:
        s = json.dumps(my_dict, sort_keys = False, ensure_ascii=False) + "\n"
        file.write(s)
    my_dict = {}
    if (i % 200) == 0:
        book.close()
        book = BookDown()
    book.getInfo(line, new_dir, new_dir_l, text)
    i = i + 1

print("Tüm linkler alındı.")