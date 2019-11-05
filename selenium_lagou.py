# -*- coding: utf-8 -*-

from selenium import webdriver
from lxml import etree
import re
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

class LagouSpider(object):
	driver_path = r"C:\Users\apple\chormdriver\chromedriver.exe"
	def __init__(self):
		self.driver = webdriver.Chrome(executable_path=LagouSpider.driver_path)
		self.url = 'https://www.lagou.com/jobs/list_python/p-city_3?px=default#filterBox'
		self.positions = []

	def run(self):
		self.driver.get(self.url)
		while True:
			source = self.driver.page_source
			WebDriverWait(driver=self.driver, timeout=10).until(EC.presence_of_element_located((By.XPATH, "//div[@class='pager_container']/span[last()]"))
				)
			self.parse_list_page(source)
			try:
				next_page = self.driver.find_element_by_xpath("//div[@class='pager_container']/span[last()]")
				if "page_next_disabled" in next_page.get_attribute("class"):
				# 判断下一页是否存在
					break
				else:
					next_page.click()
			except:
				print(source)
			time.sleep(5)

	def parse_list_page(self, source):
		html = etree.HTML(source)
		links = html.xpath("//a[@class='position_link']/@href")
		# 使用xpath提取href属性，拿到url
		for link in links:
			# print(link)
			self.request_detail_page(link)
			time.sleep(5)

	def request_detail_page(self, url):
		# self.driver.get(url)
		# 请求详细页面
		self.driver.execute_script("window.open('%s')" % url)
		self.driver.switch_to.window(self.driver.window_handles[1])
		WebDriverWait(self.driver, timeout=10).until(EC.presence_of_element_located((By.XPATH, "//h1[@class='name']"))
													)
		source = self.driver.page_source
		self.parse_detail_page(source)
		self.driver.close()
		# 关闭当前页面
		self.driver.switch_to.window(self.driver.window_handles[0])
		# 回到第一个页面


	def parse_detail_page(self, source):
		html = etree.HTML(source)
		position_name = html.xpath("//h1[@class='name']/text()")[0]
		job_request_spans = html.xpath("//dd[@class='job_request']//span")
		salary = job_request_spans[0].xpath('.//text()')[0].strip()
		city = job_request_spans[1].xpath('.//text()')[0].strip()
		city = re.sub(r"[\s/]", "", city)
		work_years = job_request_spans[2].xpath('.//text()')[0].strip()
		work_years = re.sub(r"[\s/]", "", work_years)
		education = job_request_spans[3].xpath('.//text()')[0].strip()
		education = re.sub(r"[\s/]", "", education)
		content = "".join(html.xpath("//dd[@class='job_bt']//text()")).strip()
		company = html.xpath("//em[@class='fl-cn']/text()")[0].strip()

		position = (
			'职位', position_name,
			'公司名字', company,
			'薪金', salary,
			'城市', city,
			'工作经验', work_years,
			'教育程度', education,
			'职位信息', content
		)
		self.positions.append(position)
		print(position)
		print("-------"*20)
		with open('works_information.txt', 'a', encoding='utf-8') as fp:
			for a in position:
				fp.write(str(a))
				fp.write('\n')
			fp.close()

if __name__ == '__main__':
	spider = LagouSpider()
	spider.run()