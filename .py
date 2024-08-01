import jsonlines

# Define the path to your files
input_file_path = '/Users/srisowmi/Documents/Msc Project Work/Menopause/srinath/fine_tuning_data.jsonl'
output_file_path = 'restructured_fine_tuning_data.jsonl'

# Load the data from the JSONL file
with jsonlines.open(input_file_path) as reader:
    data = [entry for entry in reader]

# Restructure the data
restructured_data = []
for entry in data:
    prompt = entry['prompt'].replace('Context: \n', '').replace('Chatbott:', 'Chatbot:')
    completion = entry['completion'].strip()
    
    restructured_entry = {
        'prompt': prompt,
        'completion': completion
    }
    restructured_data.append(restructured_entry)

# Save the restructured data to a new JSONL file
with jsonlines.open(output_file_path, mode='w') as writer:
    writer.write_all(restructured_data)

print(f"Restructured data saved to {output_file_path}")
