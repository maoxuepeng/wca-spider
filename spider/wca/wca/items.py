# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class MemberContactItem(scrapy.Item):
    """member contact info"""
    name = scrapy.Field() #	Liu Yu Juan
    title = scrapy.Field() # G.M.
    mobile_phone = scrapy.Field() # +86.177.2269.6565
    email = scrapy.Field() # louisa.liu@landingcargo.com
    msn = scrapy.Field() # 	QQ: 2850458099
    skype = scrapy.Field()
    photo_url = scrapy.Field()


class MemberItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    wca_id = scrapy.Field() #102030
    name = scrapy.Field() # Landing Cargo Service Beijing Co., Ltd. (Beijing, Head Office - Administrative support provided by Landing Cargo HongKong Limited)
    logo_url = scrapy.Field() # https://www.wcaworld.com/logos/102030.jpg
    
    country = scrapy.Field() # China
    city = scrapy.Field() # Beijing
    
    enrolled_since = scrapy.Field() # Apr 07, 2016
    membership_expires = scrapy.Field() # Apr 06, 2020
    description = scrapy.Field() # Landing Cargo Service Beijing Co., Ltd., established in 2012, is a ...
    
    address = scrapy.Field() 
    telephone = scrapy.Field() # 	+86.10.6457.6326
    fax = scrapy.Field() # +86.10.6457.2120
    emergency_call = scrapy.Field() # +86.156.5266.7168
    website = scrapy.Field()
    email = scrapy.Field()
    contact = scrapy.Field(serializer=list) # a list of MemberContactItem


