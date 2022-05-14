from facebook_scraper import get_posts
from facebook_scraper import get_posts, FacebookScraper
from facebook_scraper import get_group_info
from facebook_scraper import get_profile, get_posts_by_search
from requests.cookies import cookiejar_from_dict

cookies = {'c_user': '100067798487014', 'datr': 'qZJnYp7x6IuXV9AaELahfI-R', 'fr': '0ECE2kUBrj2rKbpbr.AWVhMQFxbPx4U9kmS45-_DNCVGE.BiZ5Kp.qJ.AAA.0.0.BiZ5LB.AWWa3D_Ukfg', 'sb': 'qZJnYgAmZVLGMBONB017QqTc', 'xs': '48%3AMOS3Drhz0ZOOLA%3A2%3A1650954924%3A-1%3A-1'}
cookies1 = {'c_user': '100077256379331', 'datr': 'q9VoYhOu7rLT763bNum5JWbK', 'fr': '08930r9t19vvK9ObL.AWWf2YmwZxjedRvVTVwrTq7VRLQ.BiaNWr.C5.AAA.0.0.BiaNWu.AWWrVq0j_WY', 'sb': 'q9VoYuWwX6NM0dRBAlsNdr5c', 'xs': '35%3Ah3Of_B4voITQ0g%3A2%3A1651037614%3A-1%3A-1'}
cookies2 = {'c_user': '100075883932859', 'datr': 'qtZoYuMOZ1VlzLV-lWqLZ9eG', 'fr': '0GEG9xWbFDAZrJPMM.AWXhHJeaDHiOcszCyWsbcA202WQ.BiaNaq.mI.AAA.0.0.BiaNar.AWWxqYv0jmI', 'sb': 'qtZoYgmnU2hHy9Mc3X0hq2hq', 'xs': '10%3ADdnGBgmDJMDRTw%3A2%3A1651037868%3A-1%3A-1'}

cookies4 = {'c_user': '100080693307667', 'datr': 'moN4YmFNdWp8irqyt3qy14Cz', 'fr': '0546Ze7QWzbTgO5T5.AWUuz7DTIENiF1cYlc-7ElLdgVg.BieIOa.9W.AAA.0.0.BieIOa.AWXsBSRxhas', 'xs': '36:0HKCauhnk3u1bw:2:1652065104:-1:-1'}

def test():
    face = FacebookScraper()
    face.session.cookies.update(cookiejar_from_dict(cookies1))
    # face.login("100081198725298", "howardsxfloyd271")
    face.set_proxy('http://{}:{}@{}:{}'.format("franz_allan+dev_mati","13d9bb5825", "85.31.49.213","30001"))
    for z in face.get_posts_by_search("авто"):
        print(z)
    for post in face.get_posts('338007373287006'):
        print(post['text'][:50])
    z['likes']
    z['comments']
    z['shares']
    z['post_url']
    z['user_id']
    z['username']
    z['user_url']
    z['page_id']
    # face = FacebookScraper()
    # face.login("100077835392612", "135xyT_AE_Hm644")
    # face.session.cookies.get_dict()
    # for post in get_posts('720002121403767', cookies=cookies2):
    #      print(post['text'])
    for post in get_posts_by_search('игра', cookies=cookies3):
        print(post['text'])
    face = FacebookScraper()
    face.login("gennadiyoa5pan@rambler.ru", "GTpM0ijRG9")
    face.session.cookies.get_dict()
    for post in face.get_posts('nintendo'):
        print(post['text'][:50])

    print(1)

if __name__ == '__main__':
    try:
        test()
    except Exception as e:
        print(e)