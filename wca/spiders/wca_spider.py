# -*- coding: utf-8 -*-

# Member spider of https://www.wcainterglobal.com

from wca.items import MemberItem
import wca.xpaths as xpaths
import scrapy
from scrapy.http import FormRequest
from scrapy.http import Request
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, Join
from scrapy.selector import Selector
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
        selector = Selector(text=response.text)

        member_item = MemberItem()
        member_item.add_value(
            'wca_id', 
            xpaths.get_member_id(selector))
        member_item.add_value(
            'name', 
            xpaths.get_member_name(selector))
        member_item.add_value(
            'logo_url',
            xpaths.get_member_logo_url(selector))
        member_item.add_value(
            'country',
            xpaths.get_member_country(selector))
        member_item.add_value(
            'city',
            xpaths.get_member_city(selector))
        member_item.add_value(
            'enrolled_since',
            xpaths.get_member_enrolled_since(selector))
        member_item.add_value(
            'membership_expires',
            xpaths.get_member_expires(selector))
        member_item.add_value(
            'description',
            xpaths.get_member_description(selector))
        member_item.add_value(
            'address',
            xpaths.get_member_address(selector))
        member_item.add_value(
            'telephone',
            xpaths.get_member_telephone(selector))
        member_item.add_value(
            'fax',
            xpaths.get_member_fax(selector))
        member_item.add_value(
            'emergency_call',
            xpaths.get_member_emergency_call(selector))
        member_item.add_value(
            'website',
            xpaths.get_member_website(selector))
        member_item.add_value(
            'email',
            xpaths.get_member_email(selector))

        member_item.add_value(
            'contact',
            xpaths.get_member_contact(selector))
        
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
