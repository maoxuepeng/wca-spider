# -*- coding: utf-8 -*-

import os
import unittest
import xpaths
from scrapy.selector import Selector
from urllib import unquote

class TestXPathsSiginPage(unittest.TestCase):
    def setUp(self):
        test_data_path = os.getenv('TEST_DATA_PATH')
        self.sigin_html = open(os.path.join(test_data_path, 'signin.html'), 'rb').read()
    
    def tearDown(self):
        pass

    def test01_get_login_url(self):
        expected_url = "https://webservice.wcaworld.com/wcasso/ssov1/LogIn?random=201907121047553650&action=&sid=7c739ae1-1584-17ef-bb36-11eb64077dad&ua=TW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzc1LjAuMzc3MC4xMDAgU2FmYXJpLzUzNy4zNg%3D%3D"
        url = xpaths.get_login_url(self.sigin_html)
        print "expected  url:%s--" % expected_url
        print "get login url:%s--" % url
        self.assertTrue(expected_url==url)

    def test02_get_login_referer(self):
        expected_referer = "https://www.wcainterglobal.com"
        referer = xpaths.get_login_referer(self.sigin_html)
        self.assertTrue(expected_referer == referer)

    def test03_get_login_remote_addr(self):
        expected_addr = "116.77.73.253"
        addr = xpaths.get_login_remote_addr(self.sigin_html)
        self.assertTrue(expected_addr == addr)

    def test04_get_login_return_url(self):
        expected_return_url = ""
        return_url = xpaths.get_login_return_url(self.sigin_html)
        self.assertTrue(expected_return_url == return_url)
    
    def test05_get_login_verify_url(self):
        expected_verify_url = "https://www.wcainterglobal.com/Account/SsoLoginResult/"
        verify_url = xpaths.get_login_verify_url(self.sigin_html)
        self.assertTrue(expected_verify_url == verify_url)

class TestXPathsMemberListFirstPage(unittest.TestCase):
    def setUp(self):
        test_data_path = os.getenv('TEST_DATA_PATH')
        self.member_list_html = open(os.path.join(test_data_path, 'member_list_first_page.html'), 'rb').read()
    
    def tearDown(self):
        pass

    def test01_get_more_result_text(self):
        expected = "CLICK HERE TO LOAD MORE RESULTS"
        value = xpaths.get_more_result_text(self.member_list_html)
        self.assertTrue(expected == value)

    def test02_get_next_member_list_page_url(self):
        expected = "https://www.wcainterglobal.com/Directory?networkId=4&pageNumber=2&pageSize=100&searchby=CountryCode&orderby=CountryCity&country=CN&city=&keyword=&lastCid=69811"
        value = xpaths.get_next_member_list_page_url(self.member_list_html)
        self.assertTrue(expected == value)
    
    def test03_get_member_links(self):
        expected_links = 100
        value = len(xpaths.get_member_links(self.member_list_html))
        self.assertTrue(expected_links == value)

class TestXPathsMemberListLastPage(unittest.TestCase):
    def setUp(self):
        test_data_path = os.getenv('TEST_DATA_PATH')
        self.member_list_html = open(os.path.join(test_data_path, 'member_list_last_page.html'), 'rb').read()
    
    def tearDown(self):
        pass

    def test01_get_more_result_text(self):
        expected = None
        value = xpaths.get_more_result_text(self.member_list_html)
        self.assertTrue(expected == value)

    def test02_get_next_member_list_page_url(self):
        expected = None
        value = xpaths.get_next_member_list_page_url(self.member_list_html)
        self.assertTrue(expected == value)

class TestXPathsMemberDetailPage(unittest.TestCase):
    def setUp(self):
        test_data_path = os.getenv('TEST_DATA_PATH')
        self.member_detail_selector = Selector(text=open(os.path.join(test_data_path, 'member_details.html'), mode='r').read())
    
    def tearDown(self):
        pass

    def test01_get_values(self):
        expected_id = "118521"
        expected_name = "Shanghai Sun Glory Shipping Co., Ltd"
        expected_logo_url = "https://www.wcaworld.com/logos/118521.jpg"
        expected_member_country = "China"
        expected_member_city = "Shanghai"
        expected_member_enrolled_since = "Apr 23, 2019"
        expected_member_expires = "Apr 22, 2020"
        expected_member_description = """SGL Shipping was established in 2007. We take every effort to provide our clients the best global sea shipping service. SGL Shipping has been awarded NVOCC Certificate by MOC and the qualification of Class A Forwarding Company by MOFCOM. In accordance with the Spirit of Contract, we provide our clients CONTAINER/BREAK BULK/LOGISTICS service for the cargo inbound and outbound China.

CONTAINER SERVICE 
SGL is the primary booking agent of shipping lines like PIL, COSCO, SEALAND, CMA, EMC, etc. with a sufficient cash flow and a good credit to meet the client’s demand for shipping space. As a leading sea freight forwarder, our service covers all major ports in China. Over the years, SGL has been making every effort to meet the diverse needs of customers for transport services, and has accumulated abundant experience in special container transport, such as special containers, dangerous goods and refrigerated container and won the trust of customers. We can also provide extended logistics services such as trucking, stuffing and Customs clearance service to our clients. 
 
BREAK BULK SERVICE
SGL has been in long-term cooperation with shipping companies including BBC Chartering, SAL, NYK, AAL, BIGLIFT, and COSCO. We are familiar with all heavy-lift carriers’ tonnage position information and can provide tailor made and most economical logistics service.

•	Customs clearance
•	port agent/competitive insurance/
•	on site loading and offloading solution for max.600mt/piece/inland Multimodal transportation 
•	40-400mt heavy lift cargo such as trucking/barge service/experienced port captain supervision
•	professional cargo lashing and covering tarpaulin. 

LOGISTICS
Having 11 years’ experience SGL keep providing clients professional and effective logistics service in China and that gains us splendid reputation on the market."""
        expected_member_address = "1707th floor,Shanghai RuiFeng Internation Tower,248 Yangshupu Road,Shanghai 200082, China"
        expected_member_telephone = "+862165680236"
        expected_member_fax = None
        expected_member_emergency_call = "+8613817983006"
        expected_member_website = "http://www.shshenghong.com"
        expected_member_email = "yvonne.zhou@shshenghong.com;op06@shshenghong.com"
        expected_member_contact = ""

        memeberid = xpaths.get_member_id(self.member_detail_selector)
        name = xpaths.get_member_name(self.member_detail_selector)
        logo_url = xpaths.get_member_logo_url(self.member_detail_selector)
        member_country = xpaths.get_member_country(self.member_detail_selector)
        member_city = xpaths.get_member_city(self.member_detail_selector)
        member_enrolled_since = xpaths.get_member_enrolled_since(self.member_detail_selector)
        member_expires = xpaths.get_member_expires(self.member_detail_selector)
        member_description = xpaths.get_member_description(self.member_detail_selector)
        member_address = xpaths.get_member_address(self.member_detail_selector)
        member_telephone = xpaths.get_member_telephone(self.member_detail_selector)
        member_fax = xpaths.get_member_fax(self.member_detail_selector)
        member_emergency_call = xpaths.get_member_emergency_call(self.member_detail_selector)
        member_website = xpaths.get_member_website(self.member_detail_selector)
        member_email = xpaths.get_member_email(self.member_detail_selector)
        member_contact = xpaths.get_member_contact(self.member_detail_selector)

        print """
        memberid=%s,\n
        name=%s,\n
        logo=%s,\n
        country=%s,\n
        city=%s,\n
        enrolled_since=%s,\n
        expires=%s,\n
        description=%s,\n
        address=%s,\n
        telephone=%s,\n
        fax=%s,\n
        emergency_call=%s,\n
        website=%s,\n
        email=%s,\n
        contact=%s,\n""" % (
        memeberid,
        name,
        logo_url,
        member_country,
        member_city,
        member_enrolled_since,
        member_expires,
        member_description,
        member_address,
        member_telephone,
        member_fax,
        member_emergency_call,
        member_website,
        member_email,
        member_contact
        )

        self.assertTrue(
            expected_id == memeberid and
            expected_name == name and
            expected_logo_url == logo_url and
            expected_member_country == member_country and
            expected_member_city == member_city and
            expected_member_enrolled_since == member_enrolled_since and
            expected_member_expires == member_expires and
            expected_member_description == member_description and
            expected_member_address == member_address and
            expected_member_telephone == member_telephone and
            expected_member_fax == member_fax and
            expected_member_emergency_call == member_emergency_call and
            expected_member_website == member_website and
            expected_member_email == member_email and
            expected_member_contact == member_contact
        )

if __name__ == '__main__':
    suit = unittest.TestSuite()
    suit.addTest(unittest.makeSuite(TestXPathsSiginPage))
    suit.addTest(unittest.makeSuite(TestXPathsMemberListFirstPage))
    suit.addTest(unittest.makeSuite(TestXPathsMemberListLastPage))
    suit.addTest(unittest.makeSuite(TestXPathsMemberDetailPage))

    runner = unittest.TextTestRunner()
    runner.run(suit)    