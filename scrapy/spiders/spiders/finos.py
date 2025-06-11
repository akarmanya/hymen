import re
from typing import List, Generator, Any
from urllib.parse import urljoin

import ftfy
import requests
import structlog

import scrapy
from scrapy import Request, Selector

from .schema import (
    FINOSCatalogue,
    RiskItem,
    RiskSection,
    MitigationItem,
    MitigationSection,
)


class FINOSSpider(scrapy.Spider):
    name = "finos"
    base_url = "https://air-governance-framework.finos.org/"
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

    def parse_risk_item(self, card_element) -> RiskItem:
        risk_id = self.clean_text(
            card_element.xpath(".//div[contains(@class, 'risk-id')]/text()").get("")
        )
        title = self.clean_text(
            card_element.xpath(".//h3[contains(@class, 'card-title')]/text()").get("")
        )
        url = urljoin(self.base_url, card_element.xpath(".//a/@href").get(""))

        content = ""
        if url:
            response = requests.get(url)
            if response.ok:
                selector = Selector(text=response.text)
                card_body = selector.xpath("//div[contains(@class, 'card-body')]")[0]
                # Extract all text content, preserving structure
                sections = []
                for element in card_body.xpath(".//*[self::h2 or self::p or self::ul]"):
                    if element.xpath("name()").get() == "h2":
                        # Add heading
                        sections.append(
                            "\n## "
                            + self.clean_text(element.xpath("text()").get(""))
                            + "\n"
                        )
                    elif element.xpath("name()").get() == "p":
                        # Add paragraph
                        sections.append(
                            self.clean_text(element.xpath("string()").get("")) + "\n"
                        )
                    elif element.xpath("name()").get() == "ul":
                        # Add list items
                        for li in element.xpath(".//li"):
                            sections.append(
                                "- "
                                + self.clean_text(li.xpath("string()").get(""))
                                + "\n"
                            )
                content = "\n".join(sections)

        return RiskItem(risk_id=risk_id, title=title, content=content, url=url)

    def parse_mitigation_item(self, card_element) -> MitigationItem:
        mitigation_id = self.clean_text(
            card_element.xpath(".//div[contains(@class, 'mitigation-id')]/text()").get(
                ""
            )
        )
        title = self.clean_text(
            card_element.xpath(".//h3[contains(@class, 'card-title')]/text()").get("")
        )
        url = urljoin(self.base_url, card_element.xpath(".//a/@href").get(""))

        content = ""
        if url:
            response = requests.get(url)
            if response.ok:
                selector = Selector(text=response.text)
                card_body = selector.xpath("//div[contains(@class, 'card-body')]")[0]
                # Extract all text content, preserving structure
                sections = []
                for element in card_body.xpath(".//*[self::h2 or self::p or self::ul]"):
                    if element.xpath("name()").get() == "h2":
                        sections.append(
                            "\n## "
                            + self.clean_text(element.xpath("text()").get(""))
                            + "\n"
                        )
                    elif element.xpath("name()").get() == "p":
                        sections.append(
                            self.clean_text(element.xpath("string()").get("")) + "\n"
                        )
                    elif element.xpath("name()").get() == "ul":
                        for li in element.xpath(".//li"):
                            sections.append(
                                "- "
                                + self.clean_text(li.xpath("string()").get(""))
                                + "\n"
                            )
                content = "\n".join(sections)

        return MitigationItem(
            mitigation_id=mitigation_id, title=title, content=content, url=url
        )

    def parse(self, response) -> Generator[FINOSCatalogue, Any, None]:
        risk_sections: List[RiskSection] = []

        # Get all sections between risk catalogue and mitigation catalogue
        risk_sections_html = response.xpath(
            "//h2[@id='risk-catalogue']/following-sibling::section[count(preceding-sibling::h2[@id='mitigation-catalogue'])=0]"
        )

        for section in risk_sections_html:
            category = self.clean_text(
                section.xpath(".//h3[contains(@class, 'category-title')]/text()").get(
                    ""
                )
            )
            risks = []
            for card in section.xpath(".//div[contains(@class, 'card')]"):
                risk = self.parse_risk_item(card)
                if risk.risk_id:
                    risks.append(risk)

            if category and risks:
                risk_sections.append(RiskSection(category=category, risks=risks))

        # Parse mitigation sections
        mitigation_sections: List[MitigationSection] = []
        mitigation_sections_html = response.xpath(
            "//h2[@id='mitigation-catalogue']/following-sibling::section"
        )

        for section in mitigation_sections_html:
            category = self.clean_text(
                section.xpath(".//h3[contains(@class, 'category-title')]/text()").get(
                    ""
                )
            )
            mitigations = []
            for card in section.xpath(".//div[contains(@class, 'card')]"):
                mitigation = self.parse_mitigation_item(card)
                if mitigation.mitigation_id:
                    mitigations.append(mitigation)

            if category and mitigations:
                mitigation_sections.append(
                    MitigationSection(category=category, mitigations=mitigations)
                )

        # Create the final catalogue
        catalogue = FINOSCatalogue(
            risk_sections=risk_sections, mitigation_sections=mitigation_sections
        )

        yield catalogue
