# -*- coding: utf-8 -*-

# Member spider of https://www.wcainterglobal.com

from wca.items import MemberItem
import wca.xpaths as xpaths
import scrapy
from scrapy.http import FormRequest
from scrapy.http import Request
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, Join
import urlparse
import os
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    handlers=[logging.FileHandler('var/log/wca_spider.log')])

class WCASpider(scrapy.spiders.Spider):
    name = 'wca_spider'
    allowed_domains = ["www.wcainterglobal.com"]
    #start_urls = []

    # start from login request
    def start_requests(self):
        # login url is https://www.wcainterglobal.com/Account/Login, there same hidden properties should retrive
        return [
            Request("https://www.wcainterglobal.com/Account/Login", callback=self._parse_login_page)
        ]

    #parse login url and inputs from page
    def _parse_login_page(self, response):
        html = response.text
        login_url = xpaths.get_login_url(html)
        referer = xpaths.get_login_referer(html)
        remote_addr = xpaths.get_login_remote_addr(html)
        returnurl = xpaths.get_login_return_url(html)
        verifyurl = xpaths.get_login_verify_url(html)

        post_headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.8,en;q=0.6",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.75 Safari/537.36",
            "Referer": "https://www.wcainterglobal.com/",
        }

        return [
            FormRequest(
                login_url, 
                formdata={
                    'referer': referer,
                    'REMOTE_ADDR': remote_addr,
                    'returnurl': returnurl,
                    'verifyurl': verifyurl,
                    'username': os.getenv('WCA_USERNAME'),
                    'password': os.getenv('WCA_PASSWORD')
                }, 
                headers=post_headers, 
                callback=self._start_crawl)
        ]

    # after login, start parse
    def _start_crawl(self, response):
        # _setup_start_urls
        start_urls = self._setup_start_urls()
        for url in start_urls:
            yield Request(url, callback=self._parse_member_list_page)
            logging.info('URL %s scheduled', url)

    def _parse_member_list_page(self, response):
        #if 'CLICK HERE TO LOAD MORE RESULTS' represent
        # yeild a h request set call back as _parse_member_list_page
        html = response.text
        more_result_text = xpaths.get_more_result_text(html)
        if 'CLICK HERE TO LOAD MORE RESULTS' == more_result_text:
            next_page_url = xpaths.get_next_member_list_page_url(html)
            # crawl next page
            yield Request(next_page_url, callback=self._parse_member_list_page)
            logging.info('Has more result, schedule next page by URL %s', next_page_url)
        
        # parse member links in reponse, crawl each member detail
        member_links = xpaths.get_member_links(html)
        for memeber_link in member_links:
            yield Request(memeber_link, callback=self._parse_member_detail_page)
            logging.info('Member link of %s scheduled', memeber_link)

    def _parse_member_detail_page(self, response):
        member_item = ItemLoader(item=MemberItem(), response=response)

        #member_contact_item = MemberContactItem()
        member_item.add_xpath(
            'wca_id', 
            '//*[@class="member_id"][1]/text()',
            MapCompose(lambda i: i.strip('ID:').strip()))
        member_item.add_xpath(
            'name', 
            '//*[@class="member_name"][1]/text()',
            MapCompose(lambda i: i.strip('ID:').strip()))
        member_item.add_xpath(
            'logo_url',
            '//*[@id="content_right"]/div[2]/div[1]/img/@src')
        member_item.add_xpath(
            'country',
            '//*[@class="office_row"][1]/div[@class="office_country"][1]/text()')
        member_item.add_xpath(
            'city',
            '//*[@class="office_row"][1]/div[@class="office_entry"][1]/a[1]/text()')
        member_item.add_xpath(
            'enrolled_since',
            '//*[@class="member_expire_mainbox"][1]/div[@class="member_expire_entry"][1]/div[@class="member_expire_value"][1]/text()')
        member_item.add_xpath(
            'membership_expires',
            '//*[@class="member_expire_mainbox"][1]/div[@class="member_expire_entry"][2]/div[@class="member_expire_value"][1]/text()')
        member_item.add_xpath(
            'description',
            '//*[@class="memberprofile_row memberprofile_detail"][1]/text()')
        member_item.add_xpath(
            'address',
            '//*[@id="content_right"]/table/tbody/tr[td[1]="Address:"]/td[2]/span[1]/text()',
            MapCompose(lambda i: i.replace('<br>', '')))
        member_item.add_xpath(
            'telephone',
            '//*[@id="content_right"]/table/tbody/tr[td[1]="Telephone:"]/td[2]/text()',
            MapCompose(lambda i: i.replace('.', '')))
        member_item.add_xpath(
            'fax',
            '//*[@id="content_right"]/table/tbody/tr[td[1]="Fax:"]/td[2]/text()',
            MapCompose(lambda i: i.replace('<br>', '')))
        member_item.add_xpath(
            'emergency_call',
            '//*[@id="content_right"]/table/tbody/tr[td[1]="Emergency Call:"]/td[2]/text()',
            MapCompose(lambda i: i.replace('<br>', '')))
        member_item.add_xpath(
            'website',
            '//*[@id="content_right"]/table/tbody/tr[td[1]="Website:"]/td[2]/a[1]/@href')
        member_item.add_xpath(
            'email',
            '//*[@id="content_right"]/table/tbody/tr[td[1]="Email:"]/td[2]/span/a/text()',
            MapCompose(unicode.strip), Join())

        member_item.add_xpath(
            'contact',
            '//*[@id="content_right"]/table/tbody/tr[td[1]="Contact:"]/following-sibling::*/td/text()',
            MapCompose(unicode.strip))
        
        return member_item

    # get the start urls from https://www.wcainterglobal.com/Directory?networkId=4...
    def _setup_start_urls(self):
        # TODO
        # get country code from: https://www.wcainterglobal.com/api/v1/countries

        # start url: https://www.wcainterglobal.com/Directory?networkId=4&pageNumber=1&pageSize=100&searchby=CountryCode&orderby=CountryCity&country=AF&city=&keyword=

        url_template = 'https://www.wcainterglobal.com/Directory?networkId=4&pageNumber=1&pageSize=100&searchby=CountryCode&orderby=CountryCity&country=%(Code)s&city=&keyword='
        #
        countries = [{"Code":"CN","Name":"China"}]
        urls = []
        for country in countries:
            url = url_template % (country)
            urls.append(url)
        return urls
