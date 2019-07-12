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

def get_member_id(member_detail_pages_selector):
    value = member_detail_pages_selector\
        .xpath('//*[@class="member_id"][1]/text()')\
        .extract_first()
    value = value.lstrip('ID:').strip()
    return value

def get_member_name(member_detail_pages_selector):
    value = member_detail_pages_selector\
        .xpath('//*[@class="member_name"][1]/text()')\
        .extract_first().strip()
    return value

def get_member_logo_url(member_detail_pages_selector):
    value = member_detail_pages_selector\
        .xpath('//*[@id="content_right"]/div[2]/div[1]/img/@src')\
        .extract_first().strip()
    return value

def get_member_country(member_detail_pages_selector):
    value = member_detail_pages_selector\
        .xpath('//*[@class="office_row"][1]/div[@class="office_country"][1]/text()')\
        .extract_first().strip()
    return value

def get_member_city(member_detail_pages_selector):
    value = member_detail_pages_selector\
        .xpath('//*[@class="office_row"][1]/div[@class="office_entry"][1]/a[1]/text()')\
        .extract_first().strip()
    return value

def get_member_enrolled_since(member_detail_pages_selector):
    value = member_detail_pages_selector\
        .xpath('//*[@class="member_expire_mainbox"][1]/div[@class="member_expire_entry"][1]/div[@class="member_expire_value"][1]/text()')\
        .extract_first().strip()
    return value

def get_member_expires(member_detail_pages_selector):
    value = member_detail_pages_selector\
        .xpath('//*[@class="member_expire_mainbox"][1]/div[@class="member_expire_entry"][2]/div[@class="member_expire_value"][1]/text()')\
        .extract_first().strip()
    return value

def get_member_description(member_detail_pages_selector):
    value = member_detail_pages_selector\
        .xpath('//*[@class="memberprofile_row memberprofile_detail"][1]/text()')\
        .extract_first().strip()
    return value

def get_member_address(member_detail_pages_selector):
    value = member_detail_pages_selector\
        .xpath('//*[@id="content_right"]/table/tbody/tr[td[1]="Address:"]/td[2]/span[1]/text()')\
        .extract_first().strip()
    return value.replace('<br>', '')

def get_member_telephone(member_detail_pages_selector):
    value = member_detail_pages_selector\
        .xpath('//*[@id="content_right"]/table/tbody/tr[td[1]="Telephone:"]/td[2]/text()')\
        .extract_first().strip()
    return value.replace('.', '')

def get_member_fax(member_detail_pages_selector):
    value = member_detail_pages_selector\
        .xpath('//*[@id="content_right"]/table/tbody/tr[td[1]="Fax:"]/td[2]/text()')\
        .extract_first().strip()
    return value.replace('.', '')

def get_member_emergency_call(member_detail_pages_selector):
    value = member_detail_pages_selector\
        .xpath('//*[@id="content_right"]/table/tbody/tr[td[1]="Emergency Call:"]/td[2]/text()')\
        .extract_first().strip()
    return value.replace('.', '')

def get_member_website(member_detail_pages_selector):
    value = member_detail_pages_selector\
        .xpath('//*[@id="content_right"]/table/tbody/tr[td[1]="Website:"]/td[2]/a[1]/@href')\
        .extract_first().strip()
    return value

def get_member_email(member_detail_pages_selector):
    value = member_detail_pages_selector\
        .xpath('//*[@id="content_right"]/table/tbody/tr[td[1]="Email:"]/td[2]/span/a/text()')\
        .extract().jion()
    return value

def get_member_contact(member_detail_pages_selector):
    value = member_detail_pages_selector\
        .xpath('//*[@id="content_right"]/table/tbody/tr[td[1]="Contact:"]/following-sibling::*/td/text()')\
        .extract().jion()
    return value.strip()