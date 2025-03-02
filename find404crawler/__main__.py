"""Script file for the find404crawler package."""

import argparse
import dataclasses
import json
import os
import re
from typing import List
import playwright.sync_api
from playwright.sync_api import sync_playwright

from find404crawler.models.urlreport import URLReport


@dataclasses.dataclass
class ScriptConfig:
    """Configuration for the crawler."""

    output_folder: str


@dataclasses.dataclass
class Scope:
    """A scope for the crawler to follow."""

    allowed_url_regexes: List[str]  # Must have at least base url
    forbidden_urls_regexes: List[str] | None = None

    def evaluate(self, url: str) -> bool:
        """
        Returns whether the url should be crawled according to this scope
        """
        if not any(
            re.findall(allowed_url_regex, url)
            for allowed_url_regex in self.allowed_url_regexes
        ):
            # No matching allowed url. Forbid it
            return False

        if any(
            re.findall(forbidden_url_regex, url)
            for forbidden_url_regex in (self.forbidden_urls_regexes or [])
        ):
            # No matching allowed url. Forbid it
            return False

        return True


class KBCrawler:
    """A simple web crawler that crawls the web starting from a set of seed URLs."""

    def __init__(self, scope: Scope):
        self.noted: List[str] = []
        self.upcoming: List[str] = []
        self.scope = scope

    def crawl(
        self,
        browser: playwright.sync_api.Browser,
        seed_urls: List[str],
        config: ScriptConfig,
    ):
        """Crawl the web starting from the seed URLs."""
        for seed_url in seed_urls:
            self.queue_url(seed_url)

        while self.upcoming:
            upcoming = self.upcoming.pop()
            print(f"Crawling {upcoming}")
            try:
                self.handle_url(browser=browser, url=upcoming, config=config)
            except Exception as exc:
                print(f"Encountered exception while handling URL '{upcoming}', {exc}")

    def handle_url(
        self, browser: playwright.sync_api.Browser, url: str, config: ScriptConfig
    ) -> None:
        """Handle a single URL."""
        report = URLReport(url=url)
        page = browser.new_page()
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=120 * 1000)
        except playwright.sync_api.TimeoutError:
            print(f"Timeout while loading {url}")
        else:
            for element in page.query_selector_all("a"):
                href = str(element.get_property("href"))
                if not href:
                    # Link without href...
                    continue

                report.add_link(url=href, in_scope=self.scope.evaluate(url=href))
                self.queue_url(href.split("#", maxsplit=1)[0])
        finally:
            page.close()

        with open(
            os.path.join(config.output_folder, "crawl-log.ndjson"),
            "a",
            encoding="utf-8",
        ) as log_h:
            # Newline delimited json
            print(json.dumps(report.to_dict()), file=log_h)

    def queue_url(self, url: str):
        """Queue a URL for crawling if it hasn't been noted before."""
        if url not in self.noted:
            print(f"Found new URL: {url}")
            self.noted.append(url)
            if self.scope.evaluate(url=url):
                self.upcoming.append(url)
            else:
                print("Out of scope...")


PARSER = argparse.ArgumentParser()
PARSER.add_argument("--output-folder", type=str, default=".")
PARSER.add_argument("urls", type=str, nargs="+")
ARGS = PARSER.parse_args()
with sync_playwright() as p:
    BROWSER = p.firefox.launch()
    PAGE = BROWSER.new_page()
    CRAWLER = KBCrawler(
        scope=Scope(
            allowed_url_regexes=[re.escape(url) for url in ARGS.urls],
            forbidden_urls_regexes=[
                # "xml-api-interface-technical-document",
                # "vulnerability-detection-update",
                # "release-notes",
            ],
        ),
    )
    CRAWLER.crawl(
        browser=BROWSER,
        seed_urls=ARGS.urls,
        config=ScriptConfig(output_folder=ARGS.output_folder),
    )
    BROWSER.close()
