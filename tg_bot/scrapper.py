from abc import ABC, abstractmethod
from typing import Optional
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fuzzywuzzy import fuzz


class Scrapper(ABC):
    @abstractmethod
    def get_top_link(self, query: str) -> Optional[str]:
        pass


class WebScrapper(Scrapper):
    search_url: str = "https://rutube.ru/search/?query="

    def __init__(self):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        self.driver = webdriver.Chrome(options=options)

    def get_top_link(self, query: str) -> Optional[str]:
        try:
            search_url = f"{self.search_url}{query}"
            self.driver.get(search_url)

            wait = WebDriverWait(self.driver, 5)
            video_elements = wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "a.wdp-link-module__link.wdp-card-description-module__title")
                )
            )

            videos = []
            for video in video_elements:
                title = video.get_attribute("title")
                href = video.get_attribute("href")
                if title and href:
                    videos.append((title, href))

            best_match = None
            highest_ratio = 0
            for title, href in videos:
                similarity = fuzz.ratio(query.lower(), title.lower())
                if similarity > highest_ratio:
                    highest_ratio = similarity
                    best_match = href

            if best_match:
                return f"https://rutube.ru{best_match}"
            else:
                return search_url

        except Exception as e:
            return search_url
        finally:
            self.driver.quit()
