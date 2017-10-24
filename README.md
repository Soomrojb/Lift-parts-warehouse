# Liftpartswarehouse Scraper
Liftpartswarehouse.com is one of the biggest parts website with over 5 million parts; this script will visit all of its available brands, do pagination and finally get basic fields.

How to use the script?
- [x] `scrapy crawl liftpartb`
- [x] `scrapy crawl liftpartb -o brands.csv -t csv`

Default fileds:
- [x] Brand Title
- [x] Brand Href
- [x] Product Title
- [x] Product Href
- [x] Breadcrumb
- [x] Part Number #
- [x] Price
- [x] Image URL
- [x] Product Short Descption
- [x] Product Details/Description

Expected future changes:
- [ ] Rolling Proxies support
- [ ] MySQLdb support
