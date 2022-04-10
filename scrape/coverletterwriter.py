import datetime
import random

import reportlab.rl_config
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate
from textblob import TextBlob

from scrape.company_result import CompanyResult
from scrape.configs import JobScrapeConfig, PersonaConfig
from scrape.dir import change_dir
from scrape.networkingasst import BusinessCard
from scrape.striptags import strip_tags

reportlab.rl_config.warnOnMissingFontGlyphs = 0


now = datetime.datetime.now()
date = now.strftime("%y%m%d")


class CoverLetterWriter:
    """Generates a cover letter."""

    def __init__(
        self,
        company: CompanyResult,
        contact: BusinessCard,
        persona: PersonaConfig,
        config: JobScrapeConfig,
    ):
        self.company = company
        self.job = company.job_name
        self.contact = contact
        self.persona = persona
        self.config = config
        self.hiring_manager = f"{self.contact.greeting} {self.contact.fullname}"
        self.pdfmetrics = pdfmetrics
        self.reference = "BuiltInNYC"
        self.letter_date = now.strftime("%B %d, %Y")
        self.letter_title = f"{date}_{self.company.company_name}_{self.persona.name}_{random.randint(0,100)}.pdf"
        self.export_dir = f"{date}_{config.export_dir}"

        self.address: str = ""
        self.intro: str = ""
        self.salut: str = ""
        self.body: str = ""
        self.outro: str = ""
        self.close: str = ""
        self.whole_letter: str = ""

        self.cover_letter = SimpleDocTemplate(
            self.letter_title,
            pagesize=letter,
            rightMargin=1 * inch,
            leftMargin=1 * inch,
            topMargin=1.25 * inch,
            bottomMargin=1.25 * inch,
            title=self.letter_title,
            author=self.persona.name,
            creator=self.persona.name,
            subject=f"{self.persona.name}'s Cover Letter for {self.company.company_name}",
        )
        self.cl_flowables: list = []
        self.styles = getSampleStyleSheet()

    def write(self):
        """write _summary_"""
        self.register_fonts()
        self.add_styles()
        self.letter_construction()

        with change_dir(self.export_dir):
            with change_dir(f"{self.company.company_name}"):
                self.make_coverletter_pdf()
                self.make_coverletter_txt()

    def compute_proficiency_matches(self):
        """compute_proficiency_matches _summary_

        Returns:
            _type_: _description_
        """
        desc: str = strip_tags(self.company.job_description)
        duties: set = {(TextBlob(desc).noun_phrases)}
        skills: set = {self.persona.skills}
        tools: set = {self.persona.tools}
        skills_matches: set[str] = duties.intersection(skills)
        tools_matches: set[str] = duties.intersection(tools)

        matched: str = str(skills_matches).strip("}{''][").replace("'", "")
        these_tools: str = str(tools_matches).strip("}{''][").title()

        if skills_matches and tools_matches:
            return f"As requested on {self.reference}, \
                I am familiar with {matched}; proficient in {these_tools}; \
                    and am willing to learn more for the {self.company.company_name} cause"
        elif len(skills_matches):
            return f"As requested on {self.reference}, \
                I am familiar with {matched}, \
                and am willing to learn more for the {self.company.company_name} cause"
        elif len(tools_matches):
            return f"As requested on {self.reference}, \
                I am proficient in {these_tools}, \
                and am willing to learn more for the {self.company.company_name} cause"
        else:
            return f"As requested on {self.reference}, \
                I am proficient in both user interface and experience design, \
                and I am always willing to learn more"

    def ingratiate(self) -> str:
        """ingratiate _summary_

        Returns:
            str: _description_
        """
        industry_type: str = f"{self.company.industries[0].lower()} industry"
        if len(self.company.adjectives) == 0:
            return f"I've heard great things about {self.company.company_name}'s impact on the {industry_type}."

        elif len(self.company.adjectives) == 1:
            return f"I've heard great things about {self.company.company_name}'s impact on the {industry_type}, \
                along with its reputation for being {self.company.adjectives[0].lower()}."

        elif len(self.company.adjectives) == 2:
            return f"I've heard great things about {self.company.company_name}'s impact on the {industry_type}, \
                along with its reputation for being {self.company.adjectives[0].lower()} and {self.company.adjectives[1].lower()}."

        elif len(self.company.adjectives) >= 3:
            return f"I've heard great things about {self.company.company_name}'s impact on the {industry_type}, \
                along with its reputation for being {self.company.adjectives[1].lower()}, \
                    {self.company.adjectives[2].lower()}, and \
                    {self.company.adjectives[0].lower()}."

    def letter_construction(self):
        """The collection of strings and variables that make up the copy of the cover letter."""
        excitement_noun: str = random.choice(self.config.excitement_words)
        ingratiation: str = self.ingratiate()
        match_statement: str = self.compute_proficiency_matches()

        self.address: str = f"<b>{self.company.company_name}</b><br />\
                            {self.company.street_address}<br />\
                            {self.company.city}, {self.company.state}<br /><br />"

        self.intro: str = f"{self.persona.name}<br />\
                        {self.letter_date}<br /><br />\
                        {self.hiring_manager},"

        self.salut: str = f"As a {self.persona.role}, I enjoy seeing how people can come together to generate design solutions.\
                My favorite part is being a resource for teams in encouraging that shared experience.\
                But the improvement that I desire now is applying that skillset to a wider variety of business challenges.\
                {ingratiation}\
                That's why I'm writing to express my interest in the <b>{self.job}</b> role at <b>{self.company.company_name}</b>\
                where I believe that my {self.persona.values} will be a major value contribution to the design team \
                at {self.company.company_name}.<br />"

        self.body: str = f'{match_statement}. I also am a Community Advisor for the Anti-Defamation League\'s new <a href="https://socialpatterns.adl.org/about/" color="blue">Social Patterns Library</a>\
                and I\'m the co-founder of the <a href="https://www.prosocialdesign.org/" color="blue">Prosocial Design Network</a>,\
                a 501(c)3 that explores how digital media might bring out the best in human nature through behavioral science.'

        self.outro: str = f'I\'d be {excitement_noun} to have the opportunity to further discuss the position and your needs for the role.\
                My phone number is {self.persona.phone_number}, and my email is {self.persona.email}.\
                My portfolio may be found at <a href="https://{self.persona.portfolio}" color="blue">{self.persona.portfolio}</a>.<br />'

        self.close: str = f"Best,<br />\
            {self.persona.name}"

        self.whole_letter: str = f"{self.address} {self.intro} {self.salut} {self.body} {self.outro} {self.close}"

    def register_fonts(self):
        """This registers the fonts for use in the PDF, querying them from the config.json file."""
        self.pdfmetrics.registerFont(TTFont("IBMPlex", self.config.font_regular))
        self.pdfmetrics.registerFont(TTFont("IBMPlexBd", self.config.font_bold))
        self.pdfmetrics.registerFont(TTFont("IBMPlexIt", self.config.font_italic))
        self.pdfmetrics.registerFont(TTFont("IBMPlexBI", self.config.font_bolditalic))
        self.pdfmetrics.registerFontFamily(
            "IBMPlex",
            normal="IBMPlex",
            bold="IBMPlexBd",
            italic="IBMPlexIT",
            boldItalic="IBMPlexBI",
        )

    def add_styles(self):
        """This registers the styles for use in the PDF."""
        self.styles.add(
            ParagraphStyle(
                "Main",
                parent=self.styles["Normal"],
                fontName="IBMPlex",
                spaceBefore=16,
                fontSize=12,
                leading=16,
                firstLineIndent=0,
            )
        )

        self.styles.add(
            ParagraphStyle("MainBody", parent=self.styles["Main"], firstLineIndent=16)
        )

        self.styles.add(
            ParagraphStyle(
                "ListItem",
                parent=self.styles["Main"],
                spaceBefore=8,
                firstLineIndent=16,
                bulletText="•",
            )
        )

    def make_coverletter_txt(self):
        """This creates the cover letter as a .txt file."""
        self.whole_letter = strip_tags(self.whole_letter)
        self.whole_letter = self.whole_letter.replace("           ", "\n")

        with open(
            f"{date}_{self.company.company_name}_CoverLetter.txt", "w", encoding="utf-8"
        ) as f:
            f.write(self.whole_letter)

    def make_coverletter_pdf(self):
        """This creates the cover letter as .pdf using the ReportLab PDF Library."""
        self.cl_flowables = [
            Paragraph(self.address, style=self.styles["Main"]),
            Paragraph(self.intro, style=self.styles["Main"]),
            Paragraph(self.salut, style=self.styles["Main"]),
            Paragraph(self.body, style=self.styles["MainBody"]),
            Paragraph(self.outro, style=self.styles["MainBody"]),
            Paragraph(self.close, style=self.styles["Main"]),
        ]

        return self.cover_letter.build(self.cl_flowables)
