from pathlib import Path
import typer
from wasabi import msg
from spacy_llm.util import assemble
import logging
import re

Arg = typer.Argument
Opt = typer.Option

class PipelineRunner:
    def __init__(self, config_path: Path, examples_path: Path, verbose: bool = True):
        self.verbose = verbose
        self.config_path = config_path
        self.examples_path = examples_path
        self.nlp = None

        self._setup()

    def _setup(self):
        msg.text(f"Loading config from {self.config_path}", show=self.verbose)
        self.nlp = assemble(self.config_path, overrides={"paths.examples": str(self.examples_path)})

    def run(self, text: str):
        doc = self.nlp(text)

        msg.text(f"Text: {doc.text}")
        msg.text(f"Entities: {[(ent.text, ent.label_) for ent in doc.ents]}")
        return doc


def run_pipeline(
    # fmt: off
    text: str = Arg("", help="Text to perform Named Entity Recognition on."),
    config_path: Path = Arg(..., help="Path to the configuration file to use."),
    examples_path: Path = Arg(..., help="Path to the examples file to use."),
    verbose: bool = Opt(True, "--verbose", "-v", help="Show extra information."),
    # fmt: on
):
    runner = PipelineRunner(config_path, examples_path, verbose)
    runner.run(text)

def infer_years_for_dates(text):
    # Pattern to match dates, capturing the date part and the optional year
    date_pattern = re.compile(r'(\d{1,2}(?:st|nd|rd|th)?\s(?:January|February|March|April|May|June|July|August|September|October|November|December))(?:\s(\d{4}))?', re.I)
    
    # Find all dates in the text
    dates = [(match.group(0), match.start(), match.end(), match.group(2)) for match in date_pattern.finditer(text)]
    
    # If no dates found, return the original text
    if not dates:
        return text
    
    # Process dates to infer missing years
    for i, (_, start, end, year) in enumerate(dates):
        if year is None:
            # Look for the nearest date with a year, searching both directions
            prev_years = [prev_year for _, _, _, prev_year in dates[:i] if prev_year is not None]
            next_years = [next_year for _, _, _, next_year in dates[i+1:] if next_year is not None]
            
            # Determine the closest year from previous or next dates
            closest_year = prev_years[-1] if prev_years else (next_years[0] if next_years else None)
            
            # If a closest year is found, replace the date without year with the inferred year
            if closest_year:
                text = text[:start] + text[start:end] + f" {closest_year}" + text[end:]
    
    return text



if __name__ == "__main__":
    typer.run(run_pipeline)
