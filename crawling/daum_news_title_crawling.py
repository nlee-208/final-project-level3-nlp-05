import argparse
from datetime import date, timedelta
import json
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from pyvirtualdisplay import Display
from tqdm import tqdm
import re


class CrawlingDaumNewsTitle:
    title_base_url = 'https://news.daum.net/breakingnews/'
    categories = {
        '사회':'society',
        '정치':'politics',
        '경제':'economic',
        '국제': 'foreign',
        '문화':'culture',
        '연예':'entertain',
        '스포츠':'sports',
        'IT':'digital'
        }
    
    def __init__(self):
        self.driver = self._get_driver()
        
    def _get_driver(self):
        '''
        selenium
        '''
        display = Display(visible=0, size=(1920, 1080))
        display.start()
        
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome('./chromedriver', chrome_options=chrome_options)
        return driver

    def _driver_wait(self):
        WebDriverWait(self.driver, 2).until(
            expected_conditions.invisibility_of_element((By.CSS_SELECTOR, "__initial_loading"))
        )

    def get_daum_news_title(self, date, category):
        json_result = {"date": date, "category": category}
        json_result["articles"] = self._get_article_title_info(date, category)
        with open(f"daum_titles_{date}_{category}.json", "w", encoding="utf-8") as f:
            json.dump(json_result, f, ensure_ascii=False)

    def _get_article_title_info(self, date, category):
        url_page_num = 1
        title_infos = []
        while True:
            print(f'{category} page {url_page_num:03d} crawling...')
            url = f"{self.title_base_url}/{self.categories[category]}?page={url_page_num}&regDate={date}"
            self.driver.get(url)
            self._driver_wait()

            bsObject = BeautifulSoup(self.driver.page_source, "html.parser")
             
            cur_page_num = re.sub(r"[^\d]+", "", bsObject.select("em.num_page")[0].text)

            if url_page_num != int(cur_page_num):
                print('finished.')
                break
            
            content = bsObject.select('#mArticle .tit_thumb a')
            news_url_list = [c['href'] for c in content]
            title_list = [c.text for c in content]
            for i in range(len(content)):
                title_infos.append({
                    "id": f"{url_page_num:03d}_{i+1:02d}",
                    "title": title_list[i],
                    "url": news_url_list[i]
                })
            url_page_num += 1
        return title_infos

def get_args():
    parser = argparse.ArgumentParser(description="crawling daum news titile.")
    parser.add_argument(
        "--date",
        default=(date.today() - timedelta(1)).strftime("%Y%m%d"),
        type=str,
        help="date of news"
    )
    parser.add_argument(
        "--category",
        default="all",
        type=str,
        help="category of news",
        choices=["all", "society", "politics", "economic", "foreign", "culture", "entertain", "sports", "digital"]
    )
    args = parser.parse_args()
    return args

def main():
    args = get_args()
    date = args.date
    crawling_obj = CrawlingDaumNewsTitle()
    if args.category == "all":
        for category in crawling_obj.categories:
            crawling_obj.get_daum_news_title(date=date, category=category)
    else:
        category = {v:k for k, v in crawling_obj.categories.items()}[args.category]
        crawling_obj.get_daum_news_title(date=date, category=category)

if __name__ == "__main__":
    main()