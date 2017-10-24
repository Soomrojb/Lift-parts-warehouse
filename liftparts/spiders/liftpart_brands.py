# -*- coding: utf-8 -*-
import scrapy, re
from bs4 import BeautifulSoup
from scrapy.utils.response import open_in_browser

LoginURL = "https://www.liftpartswarehouse.com/"

class LiftpartSpider(scrapy.Spider):
    name = 'liftpartb'
    allowed_domains = ['liftpartswarehouse.com']
    start_urls = [LoginURL]
    
    def parse(self, response):
        #open_in_browser(response)
        Soup = BeautifulSoup(response.body, "lxml")
        for Brand in Soup.select("div[id*=display_menu_2] > ul > li")[0:1]:
            Brand_Title =   Brand.select("a")[0].text
            Brand_Href  =   Brand.select("a")[0]['href']
            MetaData = {
                "Brand_Title"   : re.sub(r"\n", '', Brand_Title, re.MULTILINE),
                "Brand_Href"    : Brand_Href
            }
            yield scrapy.Request(Brand_Href, dont_filter=True, meta=MetaData, callback=self.firstpage)
    
    def firstpage(self, response):
        Soup = BeautifulSoup(response.body, "lxml")
        RwMaxRecs = response.css(".results_per_page_select option::attr(value)")[-1].extract()
        MaxRecords = re.findall(r"^(\d+)", RwMaxRecs)[0]
        Newparams = "?searching=Y&sort=13&page=1&show=" + MaxRecords
        CustomURL = response.url + Newparams
        SimplifiedUrl = response.url + "?searching=Y&sort=13&show=" + MaxRecords
        MetaData = {
            "Brand_Title"   : response.meta['Brand_Title'],
            "Brand_Href"    : response.meta['Brand_Href'],
            "SimplifiedUrl" : SimplifiedUrl
        }
        yield scrapy.Request(CustomURL, dont_filter=True, meta=MetaData, callback=self.looppages)

    def looppages(self, response):
        Soup = BeautifulSoup(response.body, "lxml")
        RawMaxPages = response.xpath("//form[@id='MainForm']/table[1]//nobr/font/b/font/b/text()")[1].extract()
        MaxPages = re.findall(r"of\s(\d+)", RawMaxPages)[0]
        # load all next pages
        for Page in range(1, int(MaxPages) + 1):
            NextPgUrl = response.meta['SimplifiedUrl'] + "&page=" + str(Page)
            yield scrapy.Request(NextPgUrl, dont_filter=True, meta=response.meta, callback=self.listpage)
        
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
                Prod_Image  =   Product.select("a[class*=__img] > img")[0]['src']
            except:
                Prod_Image  =   "-"
            MetaData = {
                "Brand_Title" : response.meta['Brand_Title'],
                "Brand_Href" : response.meta['Brand_Href'],
                "Title" : re.sub(r'\n', '', Prod_Title, re.MULTILINE),
                "Prod_Href" : Prod_Href,
                "Short_Descp" : re.sub(r'\n', '', Prod_SDesc, re.MULTILINE),
                "Image" : Prod_Image
            }
            yield scrapy.Request(Prod_Href, dont_filter=True, meta=MetaData, callback=self.productdetailpg)
            #break

    def productdetailpg(self, response):
        #open_in_browser(response)
        Soup = BeautifulSoup(response.body, "lxml")
        try:
            Prod_Details = Soup.select("span[id*=product_description]")[0].text
        except:
            Prod_Details = "-"
        try:
            Part_Number = response.xpath("//span[@class='product_code']/text()")[0].extract()
        except:
            Part_Number = "-"
        try:
            BreadCrumb = Soup.find_all("td", attrs={'class':re.compile(r"_breadcrumb_td")})[0].find_all("b")[0].text
        except:
            BreadCrumb = "-"
        try:
            Prod_Price = response.xpath("//span[@id='listOfErrorsSpan']/..//div[@class='product_productprice']/b/span/text()").extract()
        except:
            Prod_Price = "-"
        yield {
            "Brand Title" : response.meta['Brand_Title'],
            "Brand Href" : response.meta['Brand_Href'],
            "Product Title" : re.sub(r'\n', '', response.meta['Title'], re.MULTILINE),
            "Product Href" : response.meta['Prod_Href'],
            "Short Descption" : re.sub(r'\n', '', response.meta['Short_Descp'], re.MULTILINE),
            "Image" : response.meta['Image'],
            "Price" : Prod_Price,
            "Product Details" : Prod_Details,
            "Part Number" : Part_Number,
            "Breadcrumb" : BreadCrumb
        }
