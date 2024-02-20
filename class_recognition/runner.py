from class_recognition_pipeline import PipelineRunner
from pathlib import Path

runner = PipelineRunner(config_path=("./fewshot.cfg"), examples_path=("examples.jsonl"))
doc = runner.run("heart rate in the context of 'Bradycardia, also known as bradyarrhythmia, is a slow heart rate, namely, a resting heart rate of under 60 beats per minute (BPM) in adults. It is a type of cardiac arrhythmia. It seldom results in symptoms until the rate drops below 50 BPM. It sometimes results in fatigue, weakness, dizziness, and at very low rates fainting.'")

print(doc)