# -*- coding: utf-8 -*-

# Member spider of https://www.wcainterglobal.com

from wca.items import MemberItem
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
    def start_request(self):
        # login url is https://www.wcainterglobal.com/Account/Login, there same hidden properties should retrive
        return [
            Request("https://www.wcainterglobal.com/Account/Login", callback=self._parse_login_page)
        ]

    #parse login url and inputs from page
    def _parse_login_page(self, response):
        login_url = response.xpath('//*[@id="login-form"][1]/@action')
        referer = response.xpath('//*[@id="login-form"]/input[@name="referer"]/@value')
        remote_addr = response.xpath('//*[@id="login-form"]/input[@name="REMOTE_ADDR"]/@value')
        returnurl = response.xpath('//*[@id="login-form"]/input[@name="returnurl"]/@value')
        verifyurl = response.xpath('//*[@id="login-form"]/input[@name="verifyurl"]/@value')

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
        more_result_text = response.xpath('//*[@id="directory_result"]/a[not(contains(@style, "display: none;"))][1]/text()')
        if 'CLICK HERE TO LOAD MORE RESULTS' == more_result_text:
            next_page_url = response.xpath('//*[@id="directory_result"]/a[not(contains(@style, "display: none;"))][1]/@onmouseover')
            next_page_url = self._get_next_member_list_page_url(next_page_url)
            # crawl next page
            yield Request(next_page_url, callback=self._parse_member_list_page)
            logging.info('Has more result, schedule next page by URL %s', next_page_url)
        
        # parse member links in reponse, crawl each member detail
        member_links = response.xpath('//*[@id="directory_result"]/ul/li/ul/li/ul/li/a/@href').extract()
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
        #countries = [{"Code":"AF","Name":"Afghanistan"},{"Code":"AX","Name":"Aland Islands"},{"Code":"AL","Name":"Albania"},{"Code":"DZ","Name":"Algeria"},{"Code":"AS","Name":"American Samoa"},{"Code":"AD","Name":"Andorra"},{"Code":"AO","Name":"Angola"},{"Code":"AI","Name":"Anguilla"},{"Code":"AQ","Name":"Antarctica"},{"Code":"AG","Name":"Antigua And Barbuda"},{"Code":"AR","Name":"Argentina"},{"Code":"AM","Name":"Armenia"},{"Code":"AW","Name":"Aruba"},{"Code":"AU","Name":"Australia"},{"Code":"AT","Name":"Austria"},{"Code":"AZ","Name":"Azerbaijan"},{"Code":"BS","Name":"Bahamas"},{"Code":"BH","Name":"Bahrain"},{"Code":"BD","Name":"Bangladesh"},{"Code":"BB","Name":"Barbados"},{"Code":"BY","Name":"Belarus"},{"Code":"BE","Name":"Belgium"},{"Code":"BZ","Name":"Belize"},{"Code":"BJ","Name":"Benin"},{"Code":"BM","Name":"Bermuda"},{"Code":"BT","Name":"Bhutan"},{"Code":"BO","Name":"Bolivia"},{"Code":"BQ","Name":"Bonaire"},{"Code":"BA","Name":"Bosnia And Herzegovina"},{"Code":"BW","Name":"Botswana"},{"Code":"BV","Name":"Bouvet Island"},{"Code":"BR","Name":"Brazil"},{"Code":"IO","Name":"British Indian Ocean Territory"},{"Code":"BN","Name":"Brunei Darussalam"},{"Code":"BG","Name":"Bulgaria"},{"Code":"BF","Name":"Burkina Faso"},{"Code":"BI","Name":"Burundi"},{"Code":"BU","Name":"Byelorussia"},{"Code":"KH","Name":"Cambodia"},{"Code":"CM","Name":"Cameroon"},{"Code":"CA","Name":"Canada"},{"Code":"CV","Name":"Cape Verde"},{"Code":"KY","Name":"Cayman Islands"},{"Code":"CF","Name":"Central African Republic"},{"Code":"TD","Name":"Chad"},{"Code":"CL","Name":"Chile"},{"Code":"CN","Name":"China"},{"Code":"CX","Name":"Christmas Island"},{"Code":"CC","Name":"Cocos (Keeling) Islands"},{"Code":"CO","Name":"Colombia"},{"Code":"KM","Name":"Comoros"},{"Code":"CG","Name":"Congo"},{"Code":"CD","Name":"Congo, The Democratic Republic Of The"},{"Code":"CK","Name":"Cook Islands"},{"Code":"CR","Name":"Costa Rica"},{"Code":"CI","Name":"Cote D`Ivoire"},{"Code":"HR","Name":"Croatia"},{"Code":"CU","Name":"Cuba"},{"Code":"CW","Name":"Curacao"},{"Code":"CY","Name":"Cyprus"},{"Code":"CZ","Name":"Czech Republic"},{"Code":"DK","Name":"Denmark"},{"Code":"DJ","Name":"Djibouti"},{"Code":"DM","Name":"Dominica"},{"Code":"DO","Name":"Dominican Republic"},{"Code":"EC","Name":"Ecuador"},{"Code":"EG","Name":"Egypt"},{"Code":"SV","Name":"El Salvador"},{"Code":"GQ","Name":"Equatorial Guinea"},{"Code":"ER","Name":"Eritrea"},{"Code":"EE","Name":"Estonia"},{"Code":"ET","Name":"Ethiopia"},{"Code":"FK","Name":"Falkland Islands (Malvinas)"},{"Code":"FO","Name":"Faroe Islands"},{"Code":"FJ","Name":"Fiji"},{"Code":"FI","Name":"Finland"},{"Code":"FR","Name":"France"},{"Code":"GF","Name":"French Guiana"},{"Code":"PF","Name":"French Polynesia"},{"Code":"TF","Name":"French Southern Territories"},{"Code":"GA","Name":"Gabon"},{"Code":"GM","Name":"Gambia"},{"Code":"GE","Name":"Georgia"},{"Code":"DE","Name":"Germany"},{"Code":"GH","Name":"Ghana"},{"Code":"GI","Name":"Gibraltar"},{"Code":"GR","Name":"Greece"},{"Code":"GL","Name":"Greenland"},{"Code":"GD","Name":"Grenada"},{"Code":"GP","Name":"Guadeloupe"},{"Code":"GU","Name":"Guam"},{"Code":"GT","Name":"Guatemala"},{"Code":"GN","Name":"Guinea"},{"Code":"GW","Name":"Guinea-bissau"},{"Code":"GY","Name":"Guyana"},{"Code":"HT","Name":"Haiti"},{"Code":"HM","Name":"Heard Island And Mcdonald Islands"},{"Code":"VA","Name":"Holy See (Vatican City State)"},{"Code":"HN","Name":"Honduras"},{"Code":"HK","Name":"Hong Kong"},{"Code":"HU","Name":"Hungary"},{"Code":"IS","Name":"Iceland"},{"Code":"IN","Name":"India"},{"Code":"ID","Name":"Indonesia"},{"Code":"IR","Name":"Iran, Islamic Republic Of"},{"Code":"IQ","Name":"Iraq"},{"Code":"IE","Name":"Ireland"},{"Code":"IL","Name":"Israel"},{"Code":"IT","Name":"Italy"},{"Code":"JM","Name":"Jamaica"},{"Code":"JP","Name":"Japan"},{"Code":"JO","Name":"Jordan"},{"Code":"KZ","Name":"Kazakhstan"},{"Code":"KE","Name":"Kenya"},{"Code":"KI","Name":"Kiribati"},{"Code":"KP","Name":"Korea, Democratic People`S Republic Of"},{"Code":"KR","Name":"Korea, Republic Of"},{"Code":"XK","Name":"Kosovo"},{"Code":"KW","Name":"Kuwait"},{"Code":"KG","Name":"Kyrgyzstan"},{"Code":"LA","Name":"Lao People`S Democratic Republic"},{"Code":"LV","Name":"Latvia"},{"Code":"LB","Name":"Lebanon"},{"Code":"LS","Name":"Lesotho"},{"Code":"LR","Name":"Liberia"},{"Code":"LY","Name":"Libya"},{"Code":"LI","Name":"Liechtenstein"},{"Code":"LT","Name":"Lithuania"},{"Code":"LU","Name":"Luxembourg"},{"Code":"MO","Name":"Macau, China"},{"Code":"MK","Name":"Macedonia, The Former Yugoslav Republic Of"},{"Code":"MG","Name":"Madagascar"},{"Code":"MW","Name":"Malawi"},{"Code":"MY","Name":"Malaysia"},{"Code":"MV","Name":"Maldives"},{"Code":"ML","Name":"Mali"},{"Code":"MT","Name":"Malta"},{"Code":"MH","Name":"Marshall Islands"},{"Code":"MQ","Name":"Martinique"},{"Code":"MR","Name":"Mauritania"},{"Code":"MU","Name":"Mauritius"},{"Code":"YT","Name":"Mayotte"},{"Code":"MX","Name":"Mexico"},{"Code":"FM","Name":"Micronesia, Federated States Of"},{"Code":"MD","Name":"Moldova, Republic Of"},{"Code":"MC","Name":"Monaco"},{"Code":"MN","Name":"Mongolia"},{"Code":"ME","Name":"Montenegro"},{"Code":"MS","Name":"Montserrat"},{"Code":"MA","Name":"Morocco"},{"Code":"MZ","Name":"Mozambique"},{"Code":"MM","Name":"Myanmar"},{"Code":"NA","Name":"Namibia"},{"Code":"NR","Name":"Nauru"},{"Code":"NP","Name":"Nepal"},{"Code":"NL","Name":"Netherlands"},{"Code":"AN","Name":"Netherlands Antilles"},{"Code":"NC","Name":"New Caledonia"},{"Code":"NZ","Name":"New Zealand"},{"Code":"NI","Name":"Nicaragua"},{"Code":"NE","Name":"Niger"},{"Code":"NG","Name":"Nigeria"},{"Code":"NU","Name":"Niue"},{"Code":"NF","Name":"Norfolk Island"},{"Code":"MP","Name":"Northern Mariana Islands"},{"Code":"NO","Name":"Norway"},{"Code":"OM","Name":"Oman"},{"Code":"PK","Name":"Pakistan"},{"Code":"PW","Name":"Palau"},{"Code":"PS","Name":"Palestinian Territory, Occupied"},{"Code":"PA","Name":"Panama"},{"Code":"PG","Name":"Papua New Guinea"},{"Code":"PY","Name":"Paraguay"},{"Code":"PE","Name":"Peru"},{"Code":"PH","Name":"Philippines"},{"Code":"PN","Name":"Pitcairn"},{"Code":"PL","Name":"Poland"},{"Code":"PT","Name":"Portugal"},{"Code":"PR","Name":"Puerto Rico"},{"Code":"QA","Name":"Qatar"},{"Code":"RE","Name":"Reunion"},{"Code":"RO","Name":"Romania"},{"Code":"RU","Name":"Russian Federation"},{"Code":"RW","Name":"Rwanda"},{"Code":"BL","Name":"Saint Barthelmey"},{"Code":"SH","Name":"Saint Helena"},{"Code":"KN","Name":"Saint Kitts And Nevis"},{"Code":"LC","Name":"Saint Lucia"},{"Code":"PM","Name":"Saint Pierre And Miquelon"},{"Code":"TS","Name":"Saint Thomas"},{"Code":"VC","Name":"Saint Vincent And The Grenadines"},{"Code":"SP","Name":"Saipan"},{"Code":"WS","Name":"Samoa"},{"Code":"SM","Name":"San Marino"},{"Code":"ST","Name":"Sao Tome And Principe"},{"Code":"SA","Name":"Saudi Arabia"},{"Code":"SN","Name":"Senegal"},{"Code":"RS","Name":"Serbia"},{"Code":"SC","Name":"Seychelles"},{"Code":"SL","Name":"Sierra Leone"},{"Code":"SG","Name":"Singapore"},{"Code":"SX","Name":"Sint Maarten"},{"Code":"SK","Name":"Slovakia"},{"Code":"SI","Name":"Slovenia"},{"Code":"SB","Name":"Solomon Islands"},{"Code":"SO","Name":"Somalia"},{"Code":"ZA","Name":"South Africa"},{"Code":"GS","Name":"South Georgia And The South Sandwich Islands"},{"Code":"SS","Name":"South Sudan"},{"Code":"ES","Name":"Spain"},{"Code":"LK","Name":"Sri Lanka"},{"Code":"SD","Name":"Sudan"},{"Code":"SR","Name":"Suriname"},{"Code":"SJ","Name":"Svalbard And Jan Mayen"},{"Code":"SZ","Name":"Swaziland"},{"Code":"SE","Name":"Sweden"},{"Code":"CH","Name":"Switzerland"},{"Code":"SY","Name":"Syrian Arab Republic"},{"Code":"TW","Name":"Taiwan"},{"Code":"TJ","Name":"Tajikistan"},{"Code":"TZ","Name":"Tanzania, United Republic Of"},{"Code":"TH","Name":"Thailand"},{"Code":"TL","Name":"Timor-leste"},{"Code":"TG","Name":"Togo"},{"Code":"TK","Name":"Tokelau"},{"Code":"TO","Name":"Tonga"},{"Code":"TT","Name":"Trinidad And Tobago"},{"Code":"TN","Name":"Tunisia"},{"Code":"TR","Name":"Turkey"},{"Code":"TM","Name":"Turkmenistan"},{"Code":"TC","Name":"Turks And Caicos Islands"},{"Code":"TV","Name":"Tuvalu"},{"Code":"UG","Name":"Uganda"},{"Code":"UA","Name":"Ukraine"},{"Code":"AE","Name":"United Arab Emirates"},{"Code":"GB","Name":"United Kingdom"},{"Code":"UM","Name":"United States Minor Outlying Islands"},{"Code":"US","Name":"United States of America"},{"Code":"UY","Name":"Uruguay"},{"Code":"UZ","Name":"Uzbekistan"},{"Code":"VU","Name":"Vanuatu"},{"Code":"VE","Name":"Venezuela"},{"Code":"VN","Name":"Vietnam"},{"Code":"VG","Name":"Virgin Islands, British"},{"Code":"VI","Name":"Virgin Islands, U.S."},{"Code":"WF","Name":"Wallis And Futuna"},{"Code":"EH","Name":"Western Sahara"},{"Code":"YE","Name":"Yemen"},{"Code":"ZM","Name":"Zambia"},{"Code":"ZW","Name":"Zimbabwe"}]
        countries = [{"Code":"CN","Name":"China"}]
        urls = []
        for country in countries:
            url = url_template % (country)
            urls.append(url)
        return urls

    # input url is a string like: loadmoreresult('?networkId=4&pageNumber=2&pageSize=100&searchby=CountryCode&orderby=CountryCity&country=CN&city=&keyword=&lastCid=69811'); return false;
    def _get_next_member_list_page_url(self, url):
        segs = url.split("'")
        return "https://www.wcainterglobal.com/Directory" + segs[1]