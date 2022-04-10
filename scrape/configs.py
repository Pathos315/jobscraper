import json
from dataclasses import dataclass, field


@dataclass(frozen=True, order=True)
class PersonaConfig:
    ''' _summary_
    '''
    name: str
    role: str
    values: str
    my_background: str
    years: str
    services: str
    email: str
    portfolio: str
    phone_number: str
    skills: list[str] = field(default_factory=list)
    tools: list[str] = field(default_factory=list)


@dataclass
class JobScrapeConfig:
    ''' _summary_
    '''
    export_dir: str
    url_builtin: str
    brand_names: str
    surnames: str
    total_pages: int
    per_page: int
    search_query: str
    font_regular: str
    font_bold: str
    font_italic: str
    font_bolditalic: str
    header: dict = field(default_factory=dict)
    excitement_words: list[str] = field(default_factory=list)
    querystring: dict = field(default_factory=dict)
    persona: dict = field(default_factory=dict)


def read_config(config_file: str):
    with open(config_file, encoding="utf-8") as file:
        data = json.load(file)
        persona = data["persona"]
        return JobScrapeConfig(**data), PersonaConfig(**persona)


# def read_persona(config_file: str) -> PersonaConfig:
#    with open(config_file) as file:
#        data = json.load(file)
#        return PersonaConfig(**data)
