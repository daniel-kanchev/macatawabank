import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from macatawabank.items import Article


class macatawabankSpider(scrapy.Spider):
    name = 'macatawabank'
    start_urls = ['https://www.macatawabank.com/info/about-us/news']

    def parse(self, response):
        links = response.xpath(
            '//div[@class="sf_colsOut product-detail"]//div[@class="sfContentBlock"][.//a]//a/@href').getall()
        dates = response.xpath('//div[@class="sf_colsOut product-detail"]//div[@class="sfContentBlock"][.//a]/text()').getall() \
                + response.xpath(
            '//div[@class="sf_colsOut product-detail"]//div[@class="sfContentBlock"][.//a]//p/text()').getall()
        dates = [" ".join(date.split()[:-1]) for date in dates if date.strip()]
        for i, link in enumerate(links):
            yield response.follow(link, self.parse_article, cb_kwargs=dict(date=dates[i]))

    def parse_article(self, response, date):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get() or response.xpath('//h1/span/text()').get()
        if title:
            title = title.strip()

        content = response.xpath('//div[@data-placeholder-label="Main Region"]//text()').getall()
        content = [text for text in content if text.strip() and '{' not in text]
        content = "\n".join(content[2:]).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
