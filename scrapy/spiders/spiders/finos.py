import re
from typing import override

import bleach
import ftfy
import structlog
from lxml import etree, html
from pydantic import BaseModel, computed_field

import scrapy
from scrapy import Request
from scrapy.http import TextResponse

from .schema import SpiderDomain


class FINOSItem(BaseModel):
    domain: SpiderDomain = "finos"
    title: str
    url: str
    lyrics: str
    metadata: dict
    citations: list[str]

    @computed_field
    @property
    @override
    def identifier(self) -> str:
        return str(self.url)


class FINOSSpider(scrapy.Spider):
    name = "finos"
    base_url = "https://air-governance-framework.finos.org/risks/ri-4_hallucination-and-inaccurate-outputs.html"
    logger = structlog.get_logger(__name__).bind(class_name="FINOSSpider")

    def clean_text(self, text):
        # Convert to string if not already
        if not isinstance(text, str):
            text = str(text)
        # Fix broken Unicode characters
        text = ftfy.fix_text(text)
        # Replace non-breaking spaces, tabs, carriage returns, and form feeds with a space
        text = re.sub(r"[\xa0\t\r\f]", " ", text)
        # Replace multiple spaces (including those created by above) with a single space
        text = re.sub(r" +", " ", text)
        # Replace multiple newlines (with optional spaces/tabs in between) with a single newline
        text = re.sub(r" *\n+", "\n", text)
        # Remove leading/trailing whitespace and newlines
        text = text.strip()
        return text

    def start_requests(self):
        yield Request(url=self.base_url, callback=self.parse)

    def parse(self, response):
        self.logger.info("response", response=response.text)
        pass
