import json

# Path to the original output .jsonl file
input_file_path = 'class-recognition-dataset.jsonl'

# Path for the subset output .jsonl file, replace this with your specific path
output_file_subset_path = 'output_subset_results.jsonl'  # Replace with your path

# Read the .jsonl file and collect examples
unique_answers = {}
with open(input_file_path, 'r', encoding='utf-8') as file:
    for line in file:
        data = json.loads(line)
        answer = data['answer']
        # If the answer is not already in the dictionary, add it with the current line as its example
        if answer not in unique_answers:
            unique_answers[answer] = data

# Write the subset of examples with unique answers to another .jsonl file
with open(output_file_subset_path, 'w', encoding='utf-8') as outfile:
    for data in unique_answers.values():
        json_line = json.dumps(data)
        outfile.write(json_line + '\n')

print(f"Subset of unique answers has been written to {output_file_subset_path}")
