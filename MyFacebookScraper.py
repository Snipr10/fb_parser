from fb_parser_get.facebook_scraper import FacebookScraper
from fb_parser_get.facebook_scraper.exceptions import LoginError


class MyFacebookScraper(FacebookScraper):

    def is_logged_in(self) -> bool:
        try:
            self.get('https://facebook.com/settings')
            return True
        except LoginError:
            return False
