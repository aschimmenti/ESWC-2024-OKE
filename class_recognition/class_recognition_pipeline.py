import os
from pathlib import Path
from typing import Optional
import typer
from wasabi import msg
from spacy_llm.util import assemble

class PipelineRunner:
    def __init__(self, config_path: Path, examples_path: Optional[Path] = None, verbose: bool = False):
        self.config_path = config_path
        self.examples_path = examples_path
        self.verbose = verbose
    def _setup(self):
        if not self.config_path.exists():
            msg.fail(f"Config file {self.config_path} does not exist.", exits=1)
        if not self.examples_path.exists():
            msg.fail(f"Examples file {self.examples_path} does not exist.", exits=1)
        
        msg.text(f"Loading config from {self.config_path}", show=self.verbose)
        self.nlp = assemble(self.config_path, overrides={"paths.examples": str(self.examples_path)})

    def run(self, text: str):
        if not os.getenv("OPENAI_API_KEY"):
            msg.fail(
                "OPENAI_API_KEY env variable was not found. "
                "Set it by running 'export OPENAI_API_KEY=...' and try again.",
                exits=1,
            )

        msg.text(f"Loading config from {self.config_path}", show=self.verbose)
        nlp = assemble(
            self.config_path,
            overrides={} if self.examples_path is None else {"paths.examples": str(self.examples_path)},
        )
        doc = nlp(text)

        msg.text(f"Text: {doc.text}")
        msg.text(f"Categories: {doc.cats}")
        return doc

def run_pipeline(
    text: str = typer.Argument(..., help="Text to perform text categorization on."),
    config_path: Path = typer.Argument(..., help="Path to the configuration file to use."),
    examples_path: Optional[Path] = typer.Argument(None, help="Path to the examples file to use (few-shot only)."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show extra information."),
):
    runner = PipelineRunner(config_path=config_path, examples_path=examples_path, verbose=verbose)
    runner.run(text)

if __name__ == "__main__":
    typer.run(run_pipeline)
