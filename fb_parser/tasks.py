from fb_parser.celery.celery import app
from fb_parser.parser_data.data import get_datas


@app.task
def start_test():
    # todo get key
    key = 'Тест'
    get_datas(url)
    print("test")
