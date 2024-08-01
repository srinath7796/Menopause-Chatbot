import openai
import docx
import json
from flask import Flask, request, jsonify, render_template

# Set up OpenAI API key
openai.api_key = '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'

# Function to read DOCX file and return its content as plain text
def read_docx(file_path):
    doc = docx.Document(file_path)
    full_text = []
    for paragraph in doc.paragraphs:
        full_text.append(paragraph.text)
    return '\n'.join(full_text)

document_text = read_docx('/Users/srisowmi/Documents/Msc Project Work/Menopause/srinath/Documents/chat data.docx')

# Function to prepare fine-tuning data in the chat format
def prepare_finetuning_data(document_text):
    scenarios = document_text.split("Scenario ")
    training_data = []

    for scenario in scenarios[1:]:
        lines = scenario.strip().split('\n')
        conversation = []

        for line in lines[1:]:
            if line.startswith("Chatbot:"):
                role = "assistant"
                text = line.replace("Chatbot:", "").strip()
            elif line.startswith("User:"):
                role = "user"
                text = line.replace("User:", "").strip()
            else:
                continue
            
            conversation.append({"role": role, "content": text})

        if conversation:
            training_data.append({"messages": conversation})

    return training_data

# Save the fine-tuning data to a JSONL file
def save_finetuning_data(training_data, file_path):
    with open(file_path, 'w', encoding='utf-8') as f:
        for entry in training_data:
            json.dump(entry, f)
            f.write('\n')

# Prepare and save fine-tuning data
training_data = prepare_finetuning_data(document_text)
fine_tuning_file_path = 'fine_tuning_data.jsonl'
save_finetuning_data(training_data, fine_tuning_file_path)

# Function to fine-tune the GPT-3.5 Turbo model
def fine_tune_model(file_path):
    # Upload the file
    response = openai.File.create(
        file=open(file_path),
        purpose='fine-tune'
    )
    file_id = response['id']
    
    # Create the fine-tuning job
    fine_tune_response = openai.FineTuningJob.create(
        training_file=file_id,
        model="gpt-3.5-turbo"
    )
    return fine_tune_response['id']

# Fine-tune the model
fine_tune_id = fine_tune_model(fine_tuning_file_path)

# Function to generate response from GPT-3.5 Turbo
def generate_response(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message['content']

# Function to retrieve relevant content from the document
def retrieve_relevant_content(query, document_text):
    lines = document_text.split('\n')
    relevant_lines = [line for line in lines if query.lower() in line.lower()]
    return '\n'.join(relevant_lines[:5])  # Limit to the first 5 relevant lines

# Function to generate RAG response
def generate_rag_response(query):
    relevant_content = retrieve_relevant_content(query, document_text)
    prompt = f"Context:\n{relevant_content}\n\nUser: {query}\nChatbot:"
    return generate_response(prompt)

# Create Flask application
app = Flask(__name__)

# Route for home page
@app.route('/')
def home():
    return render_template('index.html')

# Route for chat endpoint
@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message')
    response = generate_rag_response(user_input)
    return jsonify({"response": response})

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
