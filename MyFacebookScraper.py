from facebook_scraper import FacebookScraper
from facebook_scraper.exceptions import LoginError


class MyFacebookScraper(FacebookScraper):
    FacebookScraper.default_headers = {
        "Accept": "*/*",
        "Connection": "keep-alive",
        "Accept-Encoding": "gzip,deflate",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/603.3.8 (KHTML, like Gecko) Version/10.1.2 Safari/603.3.8"
    }

    def is_logged_in(self) -> bool:
        try:
            self.get('https://facebook.com/settings')
            return True
        except LoginError:
            return False
