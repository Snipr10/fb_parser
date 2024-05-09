class PageClass:
    def __init__(self, raw_posts, extra_info=None):
        self.raw_posts = raw_posts
        self.extra_info = extra_info
        super().__init__()

    def __iter__(self):
        return iter(self.raw_posts)