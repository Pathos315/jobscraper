from time import perf_counter

from tqdm import tqdm

from scrape.builtin_getter import parse_results
from scrape.configs import read_config
from scrape.coverletterwriter import CoverLetterWriter
from scrape.log import logger
from scrape.networkingasst import NetworkingAssistant

config, persona = read_config("./config.json")
querystring = config.querystring
builtinnyc = config.url_builtin


def main() -> None:
    """jobscraper takes the provided querystring, searches for job results,
    and for each of those job results generates a cover letter.
    """
    start = perf_counter()
    for page in range(1, config.total_pages):
        page_dict = {"page": page}
        querystring.update(page_dict)
        company_collection = parse_results(builtinnyc, querystring, page, config)

        for idx, company in enumerate(
            tqdm(company_collection, desc="Generating Contacts")
        ):
            networkingasst = NetworkingAssistant(company=company, config=config)
            business_card = networkingasst.gratuitous_schmoozing()

            logger.info(
                f"Writing cover letter to {business_card.fullname} at {business_card.workplace} for the role of {company_collection[idx].job_name}") # type: ignore
            coverletter = CoverLetterWriter(company, contact=business_card, persona=persona, config=config)
            coverletter.write()
            continue

    elapsed = perf_counter() - start
    logger.info(f"\n[jobscraper]: Job search finished in {elapsed} seconds.\n") # type: ignore

if __name__ == "__main__":
    main()
