from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from selenium import webdriver
from time import sleep
from threading import Thread, Lock


class OlxParser:
    all_links = []

    def __init__(
        self, city: str, category="", subcategory="", speed=3, num_of_parse_pages=25
    ):
        self.num_pg = num_of_parse_pages
        self.speed = speed
        self.city = city
        self.category = category
        self.subcategory = subcategory

    def __main_page(self):
        main_pages = (
            f"https://www.olx.ua/{self.category}/{self.subcategory}/{self.city}/?page="
        )
        return main_pages

    @staticmethod
    def __parse_main_link(site):
        page = urlopen(
            Request(
                site,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0"
                },
            )
        )
        soup = BeautifulSoup(page, "html.parser")
        return soup

    def __getting_links(self, num_page):
        self.all_links += [
            i.get("href")
            for i in self.__parse_main_link(
                self.__main_page() + str(num_page)
            ).find_all(
                class_="marginright5 link linkWithHash detailsLink linkWithHashPromoted"
            )
        ]
        self.all_links += [
            i.get("href")
            for i in self.__parse_main_link(
                self.__main_page() + str(num_page)
            ).find_all(class_="marginright5 link linkWithHash detailsLink")
        ]
        print(f"Get {len(self.all_links)} links")

    def __parser_for_getting_number(self, link):
        """Open links one by one, click on 'Show number', get number and add it in list 'phones'"""
        try:
            options = webdriver.ChromeOptions()
            options.add_argument("--headless")
            options.add_argument("--ignore-certificate-errors")
            browser = webdriver.Chrome(options=options)
            browser.get(link)
            browser.find_element_by_class_name("xx-large").click()
            lock = Lock()
            with lock:
                self.phones.append(browser.find_element_by_class_name("xx-large").text)
            print(f"Get {len(self.phones)} phones")
            browser.close()
        except:
            print("Deleted or without phone")

    phones = []

    def start(self):
        for i in range(1, self.num_pg + 1):
            t1 = Thread(target=self.__getting_links, args=(i,))
            t1.start()
        t1.join()

        for link in self.all_links:
            t2 = Thread(target=self.__parser_for_getting_number, args=(link,))
            t2.start()
            sleep(self.speed)
        t2.join()

        self.phones = list(set(self.phones))

        with open(f"{self.city}.txt", 'a') as my_file:
            self.phones = map(lambda x: x + '\n', self.phones)
            my_file.writelines(self.phones)

