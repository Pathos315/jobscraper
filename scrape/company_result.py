from dataclasses import dataclass, field


@dataclass(frozen=True, order=True)
class CompanyResult:
    ''' dataclass of the company
    '''
    inner_id: int
    alias: str
    company_name: str
    company_desc: str
    job_name: str
    job_description: str
    url: str
    twitter: str
    email: str
    street_address: str
    suite: str
    city: str
    state: str
    zip: str
    industries: list[str] = field(default_factory=list)
    adjectives: list[str] = field(default_factory=list)
