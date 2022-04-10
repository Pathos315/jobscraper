from json import loads
from json.decoder import JSONDecodeError
from time import sleep
from typing import Any, Optional

from bs4 import BeautifulSoup
from requests import get
from requests.exceptions import HTTPError, RequestException

from scrape.log import logger


def webscrape_results(
    target_url: str, run_beautiful_soup: bool = False, querystring: Optional[str] = None
) -> Any:
    """webscrape_results takes a target_url, id and querystring to extract results for further parsing purposes.

    Args:
        - target_url (str): a website to be scraped
        - id (int, optional): an ID that determines the output.
            1 is for JSON scraping.
            2 is for HTML scraping with BeautifulSoup.
        Defaults to 1.
        - querystring (Optional[str], optional): A querystring to govern the requested results. Defaults to None.

    Returns:
        Any: Is either text from JSON, text from BeautifulSoup, or None if no results were found.
    """
    sleep(2)
    try:
        r = get(target_url, params=querystring)
        if r.ok:
            response_text = r.text
            try:
                if not run_beautiful_soup:
                    return loads(response_text)
                elif run_beautiful_soup:
                    return BeautifulSoup(response_text, "html.parser")
            except (
                JSONDecodeError,
                RequestException,
                HTTPError,
                AttributeError,
            ) as exception:
                logger.warning(
                    f"[jobscraper] An error has occurred, moving to next item in sequence.\
                    Cause of error: {exception}"
                )
        else:
            logger.debug(r.status_code)
    except (JSONDecodeError, RequestException, HTTPError, AttributeError) as exception:
        logger.warning(
            f"[jobscraper] An error has occurred, moving to next item in sequence.\
            Cause of error: {exception}"
        )
