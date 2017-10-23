# -*- coding: utf-8 -*-
import scrapy, re
from bs4 import BeautifulSoup
from scrapy.utils.response import open_in_browser

LoginURL = "https://www.liftpartswarehouse.com/login.asp"
Credentials = ['', '']

class LiftpartSpider(scrapy.Spider):
    name = 'liftpart'
    allowed_domains = ['liftpartswarehouse.com']
    start_urls = [LoginURL]

    def parse(self, response):
        #open_in_browser(response)
        FormData = {
            'email' : Credentials[0],
            'password' : Credentials[1],
            'CustomerNewOld' : 'old',
            'imageField2.x' : '65',
            'imageField2.y' : '16'
        }

        Headers = {
            'Host' : 'www.liftpartswarehouse.com',
            'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:56.0) Gecko/20100101 Firefox/56.0',
            'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language' : 'en-US,en;q=0.5',
            'Accept-Encoding' : 'gzip, deflate, br',
            'Content-Type' : 'application/x-www-form-urlencoded',
            'Referer' : LoginURL,
            'Connection' : 'keep-alive',
            'Cookie' : response.headers.getlist('Set-Cookie'),
            'Upgrade-Insecure-Requests' : '1'
        }
        yield scrapy.FormRequest.from_response(response, method="POST", formdata=FormData, headers=Headers, callback=self.afterlogin)
    
    def afterlogin(self, response):
        #open_in_browser(response)
        Soup = BeautifulSoup(response.body, "lxml")
        for Category in Soup.select("div[id*=display_menu_3] > ul > li"):
            Cat_Title   =   Category.select("a")[0].text
            Cat_Href    =   Category.select("a")[0]['href']
            MetaData = {
                "Categ_Title"   : re.sub(r"\n", '', Cat_Title, re.MULTILINE),
                "Categ_Href"    : Cat_Href
            }
            yield scrapy.Request(Cat_Href, dont_filter=True, meta=MetaData, callback=self.listpage)
    
    def listpage(self, response):
        Soup = BeautifulSoup(response.body, "lxml")
        for Product in Soup.select("div[class*=v-product-grid] > div[class*=v-product]"):
            Prod_Title  =   Product.select("a[class*=__title]")[0].text
            Prod_Href  =   Product.select("a[class*=__title]")[0]['href']
            try:
                Prod_SDesc  =   Product.select("p[class*=__desc]")[0].text
            except:
                Prod_SDesc  =   "-"
            try:
                Prod_Price  =   Product.select("div[class*=_productprice] b")[0].text
            except:
                Prod_Price  =   "-"
            try:
                Prod_Image  =   Product.select("a[class*=__img] > img")[0]['src']
            except:
                Prod_Image  =   "-"
            MetaData = {
                "Categ_Title" : response.meta['Categ_Title'],
                "Categ_Href" : response.meta['Categ_Href'],
                "Title" : re.sub(r'\n', '', Prod_Title, re.MULTILINE),
                "Prod_Href" : Prod_Href,
                "Short_Descp" : re.sub(r'\n', '', Prod_SDesc, re.MULTILINE),
                "Image" : Prod_Image,
                "Price" : Prod_Price
            }
            yield scrapy.Request(Prod_Href, dont_filter=True, meta=MetaData, callback=self.productpage)

    def productpage(self, response):
        Soup = BeautifulSoup(response.body, "lxml")
        try:
            Prod_Details = Soup.select("span[id*=product_description]")[0].text
        except:
            Prod_Details = "-"
        yield {
            "Category Title" : response.meta['Categ_Title'],
            "Category Href" : response.meta['Categ_Href'],
            "Product Title" : re.sub(r'\n', '', response.meta['Title'], re.MULTILINE),
            "Product Href" : response.meta['Prod_Href'],
            "Short Descption" : re.sub(r'\n', '', response.meta['Short_Descp'], re.MULTILINE),
            "Image" : response.meta['Image'],
            "Price" : response.meta['Price'],
            "Product Details" : Prod_Details
        }
