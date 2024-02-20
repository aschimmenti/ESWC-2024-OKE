from ent_classification_pipeline import PipelineRunner, infer_years_for_dates
import re



runner = PipelineRunner(config_path="./fewshot.cfg", examples_path="./examples.json")
text = "The Italian Communist Party was a radical-left political party in Italy, and it was the largest party of the Italian left."
text = infer_years_for_dates(text)
print(text)
doc = runner.run(text)



for ent in doc.ents:
    print(f"{ent.text} (Start: {ent.start_char}, End: {ent.end_char})")

