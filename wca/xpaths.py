# -*- coding: utf-8 -*-

# xpath utils for wca spiders.
# use seperate xpath utils is easy for testing the xpath functions, which is the core processes of the data crawled.

from scrapy.selector import Selector

## parse login page

def get_login_url(login_page):
    return Selector(text=login_page)\
        .xpath('//*[@id="login-form"][1]/@action').extract_first()

def get_login_referer(login_page):
    return Selector(text=login_page)\
        .xpath('//*[@id="login-form"]/input[@name="referer"]/@value')\
        .extract_first()

def get_login_remote_addr(login_page):
    return Selector(text=login_page)\
        .xpath('//*[@id="login-form"]/input[@name="REMOTE_ADDR"]/@value')\
        .extract_first()

def get_login_return_url(login_page):
    return Selector(text=login_page)\
        .xpath('//*[@id="login-form"]/input[@name="returnurl"]/@value')\
        .extract_first()

def get_login_verify_url(login_page):
    return Selector(text=login_page)\
        .xpath('//*[@id="login-form"]/input[@name="verifyurl"]/@value')\
        .extract_first()

## parse member list page

def get_more_result_text(member_list_page):
    return Selector(text=member_list_page)\
        .xpath('//*[@id="directory_result"]/a[not(contains(@style, "display: none;"))][1]/text()')\
        .extract_first()

def get_next_member_list_page_url(member_list_page):
    url =  Selector(text=member_list_page)\
        .xpath('//*[@id="directory_result"]/a[not(contains(@style, "display: none;"))][1]/@onmouseover')\
        .extract_first()
    return _get_next_member_list_page_url(url)

def get_member_links(member_list_page):
    return Selector(text=member_list_page)\
        .xpath('//*[@id="directory_result"]/ul/li/ul/li/ul/li/a/@href')\
        .extract()

# input url is a string like: loadmoreresult('?networkId=4&pageNumber=2&pageSize=100&searchby=CountryCode&orderby=CountryCity&country=CN&city=&keyword=&lastCid=69811'); return false;
def _get_next_member_list_page_url(url):
    segs = url.split("'")
    return "https://www.wcainterglobal.com/Directory" + segs[1]

## parse memeber detail page

def get_member_id(member_detail_page):
    value = Selector(text=member_detail_page)\
        .xpath('//*[@class="member_id"][1]/text()')\
        .extract_first()
    value = value.lstrip('ID:').strip()
    return value