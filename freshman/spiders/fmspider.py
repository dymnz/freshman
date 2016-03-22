from scrapy.spiders import Spider
from scrapy.selector import HtmlXPathSelector, Selector
from freshman.items import FreshmanItem
from scrapy.http import Request
import re

class MySpider (Spider):

	name = "freshman"
	allowed_domains = ["freshman.tw"]
	start_urls = ["http://freshman.tw/cross/103/"]
	crawledLinks 	= []
	cursor = 0
	def parse(self, response):
		hxs = Selector(response)
		links = hxs.xpath('//table[@id="cross_dept_list"]/tbody/tr/td[3]/a/@href').extract()
		
		linkPattern = re.compile("^(?:ftp|http|https):\/\/(?:[\w\.\-\+]+:{0,1}[\w\.\-\+]*@)?(?:[a-z0-9\-\.]+)(?::[0-9]+)?(?:\/|\/(?:[\w#!:\.\?\+=&amp;%@!\-\/\(\)]+)|\?(?:[\w#!:\.\?\+=&amp;%@!\-\/\(\)]+))?$")

		links = ['http://freshman.tw/cross/103/' + i for i in links]

 		for link in links:
			if linkPattern.match(link) and not (link in self.crawledLinks):
				self.crawledLinks.append(link)
				yield Request(link, self.parse)

 		links = hxs.xpath('//ul[@id="cross_index"]/li[@class = "ok"]/a/@href').extract()

		linkPattern = re.compile("^(?:ftp|http|https):\/\/(?:[\w\.\-\+]+:{0,1}[\w\.\-\+]*@)?(?:[a-z0-9\-\.]+)(?::[0-9]+)?(?:\/|\/(?:[\w#!:\.\?\+=&amp;%@!\-\/\(\)]+)|\?(?:[\w#!:\.\?\+=&amp;%@!\-\/\(\)]+))?$")

		links = ['http://freshman.tw/' + i for i in links]

 		for link in links:
			if linkPattern.match(link) and not (link in self.crawledLinks):
				self.crawledLinks.append(link)
				yield Request(link, self.parse)

		#//div[@id="content"]/div[@id="content-left"]/table[@id = "cross_dept_list"]/tbody/tr/td/text()
		
		depts = hxs.xpath('//div[@id="content-left"]/div[1]/a/following-sibling::text()').extract()
		schools = hxs.xpath('//div[@id="content-left"]/div[1]/a/text()').extract()
		idNums = hxs.xpath('//table[@id="cross_dept"]/tbody/tr/td[@rowspan]/span[@class="number"]/text()').extract()
		#names = hxs.xpath('//table[@id="cross_dept"]/tbody/tr/td[@rowspan][3]/text()').extract()
		rowspans = hxs.xpath('//table[@id="cross_dept"]/tbody/tr/td[@rowspan][1]/@rowspan').extract()
		otherDepts = hxs.xpath('//table[@id="cross_dept"]/tbody/tr/td[@class="left"]/a/text()').extract()
		
		if len(schools)!=0:
			self.cursor = 0

		items = []
		item = None
		for i in range(0, len(idNums)):
			item = FreshmanItem() 	
			item["idNum"] = idNums[i]

			rows = int(rowspans[i])
			temp = []

			s = '//table[@id="cross_dept"]/tbody/tr[' + str(1+self.cursor) +']/td[@rowspan][3]/text()'

			names = hxs.xpath(s).extract()
			if names:
				item["name"] = names[0]
			else:
				item["name"] = "N/A"
			
			for r in range (0,rows):
				temp.append(otherDepts[self.cursor])
				crown = hxs.xpath('//table[@id="cross_dept"]/tbody/tr[' + str(1+self.cursor) +']/td[@class = "left"]/a/span[@class = "crown"]').extract()
				if len(crown)!=0 :
					dept = hxs.xpath('//table[@id="cross_dept"]/tbody/tr[' + str(1+self.cursor) +']/td[@class = "left"]/a/text()').extract()
					item["dept"] = dept[0]
				else:
					dept = hxs.xpath('//table[@id="cross_dept"]/tbody/tr[' + str(1+self.cursor) +']/td[@class = "left"]/span[@class = "crown"]/following-sibling::a/text()').extract()
					if len(dept)!=0 :
						item["dept"] = dept[0]


				self.cursor+=1			
			item['other'] = temp	
				
			items.append(item)

		for item in items:
			yield item
