import os
from pathlib import Path
from typing import Optional

import typer
from wasabi import msg

from spacy_llm.util import assemble

Arg = typer.Argument
Opt = typer.Option


def run_pipeline(
    # fmt: off
    text: str,
    config_path: str,
    examples_path: str = None,
    verbose: bool = False,
):
    # Convert string paths to Path objects if not already
    config_path = Path(config_path)
    examples_path = Path(examples_path) if examples_path else None
    
    if not os.getenv("OPENAI_API_KEY", None):
        msg.fail(
            "OPENAI_API_KEY env variable was not found. "
            "Set it by running 'export OPENAI_API_KEY=...' and try again.",
            exits=1,
        )

    msg.text(f"Loading config from {config_path}", show=verbose)
    nlp = assemble(
        config_path,
        overrides={}
        if examples_path is None
        else {"paths.examples": str(examples_path)},
    )

    doc = nlp(text)

    return doc

def main(
    text: str = typer.Argument(...),
    config_path: Path = typer.Argument(...),
    examples_path: Optional[Path] = typer.Argument(None),
    verbose: bool = typer.Option(False),
):
    run_pipeline(text, config_path, examples_path, verbose)

if __name__ == "__main__":
    typer.run(main)