import re
from contextlib import suppress
from dataclasses import dataclass

from bs4 import BeautifulSoup
from googlesearch import search
from nltk.corpus import names, webtext
from requests.exceptions import HTTPError, ProxyError, RequestException, Timeout
from textblob import TextBlob
from tld import get_tld

from scrape.company_result import CompanyResult
from scrape.configs import JobScrapeConfig
from scrape.log import logger
from scrape.web_scraper import webscrape_results

FIRST_NAMES: set[str] = names.words()
WEBTEXT: set[str] = webtext.words()


@dataclass(order=True)
class BusinessCard:
    """_summary_"""

    greeting: str
    fname: str
    surname: str
    fullname: str
    workplace: str


class NetworkingAssistant:
    """_summary_"""

    def __init__(
        self,
        company: CompanyResult,
        config: JobScrapeConfig,
    ):
        self.company = company
        self.config = config
        self.search_query = self.config.search_query
        self.linkedin_uri = "linkedin.com"
        self.wiza_uri = "https://wiza.co/d/"
        self.twitter_uri = "https://twitter.com/"
        self.facebook_uri = "facebook.com/"

        with open(config.brand_names, "r", encoding="utf8") as f:
            brand_names = set(f.readlines())
            self.set_of_brandnames: set[str] = {
                brand.strip("\n") for brand in brand_names
            }

        self.set_of_firstnames = FIRST_NAMES
        self.greeting: str = "To"
        self.first: str = "Whom It"
        self.last: str = "May Concern"

    def gratuitous_schmoozing(self) -> BusinessCard:
        """gratuitous_schmoozing searches for contact information based on urls and source page data.

        Returns:
            BusinessCard: A dataclass containing the contact's contact information and company.
        """

        search_results = self.seeking_networking_info()
        for link in search_results:
            logger.info(f"\nGetting: {link} | {self.company.company_name}\n")

            if self.linkedin_uri in link:
                (
                    self.greeting,
                    self.first,
                    self.last,
                ) = self.fetch_names_from_linkedin_urls(link)

            elif str(link).startswith(self.wiza_uri):
                logger.error(f"Skipping: {link} as it is a wiza url")

            elif str(link).startswith(self.twitter_uri):
                logger.error(f"Skipping: {link} as it is a Twitter url")

            elif self.facebook_uri in link:
                logger.error(f"Skipping: {link} as it is a Facebook url")

            elif len([brand for brand in self.set_of_brandnames if brand in link]) != 0:
                logger.debug("brand matches found")
                try:
                    response = webscrape_results(link, id=2)
                    (
                        self.greeting,
                        self.first,
                        self.last,
                    ) = self.fetch_names_from_page_sources(response)
                except (
                    TypeError,
                    HTTPError,
                    ConnectionError,
                    ProxyError,
                    Timeout,
                    IndexError,
                    ValueError,
                    RequestException,
                ) as error_found:
                    logger.error(error_found)

            elif len([brand for brand in self.set_of_brandnames if brand in link]) == 0:
                logger.debug("no brand matches found")
                username = get_tld(link, fail_silently=True, as_object=True).domain
                (
                    self.greeting,
                    self.first,
                    self.last,
                ) = self.compare_username_against_firstnames_set(username)

            else:
                try:
                    response = webscrape_results(link, id=2)
                    (
                        self.greeting,
                        self.first,
                        self.last,
                    ) = self.fetch_names_from_page_sources(response)
                except (
                    TypeError,
                    HTTPError,
                    ConnectionError,
                    ProxyError,
                    Timeout,
                    IndexError,
                    ValueError,
                    RequestException,
                ) as error_found:
                    logger.error(error_found)

            contact_card = BusinessCard(
                greeting=self.greeting,
                fname=self.first,
                surname=self.last,
                fullname=f"{self.first} {self.last}",
                workplace=self.company.company_name,
            )
            return contact_card

    def seeking_networking_info(self):
        """seeking_networking_info searches google for urls matching its provided search query.

        Returns:
            A Generator that yields URL paths to be assessed or requested.
        """
        search_results = search(
            query=f'"{self.company.company_name}" \
                            {self.search_query}',
            start=0,
            stop=3,
            pause=4,
            country="US",
            verify_ssl=False,
        )
        return search_results

    def fetch_names_from_page_sources(
        self, soup: BeautifulSoup
    ) -> tuple[str, str, str]:
        """fetch_names_from_page_sources takes a page source object from BeautifulSoup
            and from it extracts a self.first and self.last name.

        Args:
            soup (BeautifulSoup): a BeautifulSoup object that contains the page source info to be assessed.

        Returns:
            tuple[str,str]: A tuple containing a self.first and self.last name.
        """

        all_text = TextBlob(soup.text)
        self.entire_body = [
            str(word) for word in all_text.words if str(word).lower() not in WEBTEXT
        ]
        self.first_names = [
            word
            for word in self.entire_body
            if word.title() in self.set_of_firstnames and len(word)
        ]

        try:
            self.first = max(self.first_names, key=len)
        except ValueError as error_found:
            logger.error(error_found)
            pass

        with suppress(TypeError, IndexError):
            full_names = next_grams(self.entire_body, self.first)
            logger.info(full_names)
            for name in full_names:
                logger.info(name)
                if name[1] in self.set_of_brandnames:
                    logger.info(
                        f"{name} is for a brand, or is otherwise invalid. We encourage further review. Proceeding to next name."
                    )
                elif isinstance(name[1], type(None)):
                    logger.info(f"{name} is not a name.")
                self.greeting, self.first, self.last = "Dear", name[0], name[1]
                return self.greeting, self.first, self.last

    def fetch_names_from_linkedin_urls(self, link: str) -> tuple[str, str, str]:
        """fetch_names_from_linkedin_urls takes a URL from LinkedIn and, assuming it is a vanity sting, extracts the name accordingly.

        Args:
            link (str): A LinkedIn URL

        Returns:
            tuple[str,str,str]: A tuple containing a self.greeting, self.first, and self.last name.
        """
        logger.info(link)

        # split up linkedin url so that the vanity content is on the right
        if "/in/" in link:
            __prefix, __sep, username = link.partition("/in/")
            logger.info(username)

            if username.split("/"):
                username, *_ = username.split("/")
                logger.info(username)

            if username.split("?"):
                username, *_ = username.split("?")
                logger.info(username)

            username = username.strip()

        else:
            username = get_tld(link, fail_silently=True, as_object=True).domain
            username = str(username).strip()
            (
                self.greeting,
                self.first,
                self.last,
            ) = self.compare_username_against_firstnames_set(username)
            return self.greeting, self.first, self.last

        # split out the vanity url into a list. the self.first part of the url will almost definitely have it.
        counter = username.count("-")
        logger.info(f"{counter}-dashes found in username: \n {username}")

        if counter == int(0):
            (
                self.greeting,
                self.first,
                self.last,
            ) = self.compare_username_against_firstnames_set(username)

        elif counter == int(1):
            self.first, self.last = username.split("-", maxsplit=1)
            self.greeting, self.first, self.last = (
                "Dear",
                self.first.title(),
                self.last.title(),
            )

        elif counter >= int(2):
            self.first, middle, self.last, *_ = username.split("-", maxsplit=counter)
            if re.findall(r"[0-9]+", self.last):
                self.last = middle
            else:
                self.first.join(f" {middle}")
                # if the titlecase matches, then it's a match and we can return the result
            self.greeting, self.first, self.last = (
                "Dear",
                self.first.title(),
                self.last.title(),
            )

        return self.greeting, self.first, self.last

    def compare_username_against_firstnames_set(self, username: str):
        self.greeting = "Dear"
        first_candidates = [
            first_name.strip()
            for first_name in self.set_of_firstnames
            if first_name.lower() in username and username.find(first_name.lower()) == 0
        ]

        if (
            len(first_candidates) == 1
        ):  # if only one candidate match found, that's the only match so it gets returned
            self.first = first_candidates[0].title()
            self.last = str(username[len(self.first) + 1 :]).title()
            return self.greeting, self.first, self.last

        elif (
            len(first_candidates) >= 2
        ):  # if multiple matches found, then go for the longest one as that's likely to be the whole name
            logger.info(first_candidates)
            self.first = max(first_candidates, key=len).title()
            logger.info(self.first)
            self.last = str(username[len(self.first) :]).title()
            logger.info(self.last)
            return self.greeting, self.first, self.last

        else:  # if no other matches, but a username is present, split that username down the middle as close as possible and edit it later.
            _fname_len = round(len(username) / 2)
            self.first, self.last = (
                username[:_fname_len].title(),
                username[_fname_len - 1 :].title(),
            )
            return self.greeting, self.first, self.last


def next_grams(
    target_list: list, target_name: str, n: int = 1
) -> list[tuple[str, str]]:
    """next_grams [summary]

    Args:
        target_list (list): [description]
        target_name (str): [description]
        n (int, optional): [description]. Defaults to 1.

    Returns:
        list[tuple[str,str]]: Return a list of n-grams (tuples of n successive words) for this
    blob, which in this case is the self.first and self.last name.
    """
    return [
        (target_list[i], (camel_case_split(str(target_list[i + n])))[0])
        for i, word in enumerate(target_list)
        if word is target_name
    ]


def camel_case_split(text: str) -> list:
    """camel_case_split splits strings if they're in CamelCase and need to be not Camel Case.

    Args:
        str (str): The target string to be split.

    Returns:
        list: A list of the words split up on account of being Camel Cased.
    """
    return re.findall(r"[A-Z](?:[a-z]+|[A-Z]*(?=[A-Z]|$))", text)
