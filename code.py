import json
import time
import matplotlib.pyplot as plt
import numpy as np
from openai import OpenAI

# Define the models you want to benchmark
models = [
    "meta-llama/Meta-Llama-3.1-405B-Instruct",  # Replace with your preferred models
    "mistralai/Mistral-Nemo-Instruct-2407",
    "google/gemma-2-27b-it",
    "meta-llama/Meta-Llama-3.1-8B-Instruct",
    "google/gemma-2-9b-it"

]

# Create an OpenAI client with your deepinfra token and endpoint
openai = OpenAI(
    api_key="$API_KEY",  # Replace with your API key
    base_url="https://api.deepinfra.com/v1/openai",
)

def correct_json(model, malformed_json):
    """Use the specified model to correct the JSON."""
    chat_completion = openai.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "Correct the following JSON and send only JSON formatted output without any message."},
            {"role": "user", "content": malformed_json},
        ],
    )
    return chat_completion.choices[0].message.content

def extract_json(text):
    """Extract JSON object from the text by identifying the first valid JSON structure."""
    start = text.find('{')
    if start == -1:
        return None

    brace_count = 0
    for i in range(start, len(text)):
        if text[i] == '{':
            brace_count += 1
        elif text[i] == '}':
            brace_count -= 1

        if brace_count == 0:
            try:
                json_str = text[start:i + 1]
                json.loads(json_str)
                return json_str
            except json.JSONDecodeError:
                continue
    return None

def normalize_json(json_str):
    """Normalize JSON string to remove extra whitespace and ensure consistent formatting."""
    try:
        return json.dumps(json.loads(json_str), sort_keys=True)
    except json.JSONDecodeError:
        return None

def compare_json_objects(expected, actual):
    """Compare two JSON objects for equality after normalization."""
    normalized_expected = normalize_json(expected)
    normalized_actual = normalize_json(actual)
    return normalized_expected == normalized_actual

def benchmark_accuracy_for_model(model, test_cases):
    correct_count = 0
    total_cases = len(test_cases)
    start_time = time.time()

    for i, (malformed_json, correct_json_str) in enumerate(test_cases):
        model_response = correct_json(model, malformed_json)
        corrected_json = extract_json(model_response)

        if corrected_json is not None and compare_json_objects(correct_json_str, corrected_json):
            correct_count += 1

        if corrected_json is None:
            result = "Incorrect"
        else:
            if compare_json_objects(correct_json_str, corrected_json):

                result = "Correct"
            else:
                result = "Incorrect"

        print(f"Test Case {i+1}: {result}")
        print("Model Response:")
        print(model_response)
        print("malformed json")
        print(malformed_json)
        print("Expected JSON:")
        print(correct_json_str)
        print("-----")

    end_time = time.time()
    accuracy = (correct_count / total_cases) * 100
    total_time = end_time - start_time
    print(f"Overall Accuracy: {accuracy:.2f}% across {total_cases} test cases")
    print(f"Total Time Taken: {total_time:.2f} seconds")
    return accuracy

def benchmark_all_models(models, test_cases):
    model_accuracies = {}

    for model in models:
        print(f"Benchmarking model: {model}")
        accuracy = benchmark_accuracy_for_model(model, test_cases)
        model_accuracies[model] = accuracy
        print(f"Accuracy for {model}: {accuracy:.2f}%")

    return model_accuracies

def plot_accuracies(model_accuracies):
    models = list(model_accuracies.keys())
    accuracies = list(model_accuracies.values())


    plt.figure(figsize=(10, 6))
    bars = plt.bar(models, accuracies, color='blue', edgecolor='black')

    plt.xlabel('Models', fontsize=14)
    plt.ylabel('Accuracy (%)', fontsize=14)
    plt.title('Model Accuracy Comparison', fontsize=16, weight='bold')

    # Add accuracy labels on top of each bar
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + 0.5, f'{yval:.2f}%', ha='center', va='bottom', fontsize=12)

    plt.xticks(rotation=45, ha='right', fontsize=12)
    plt.ylim(0, 100)
    plt.tight_layout()
    plt.show()


# Define your test cases
test_cases = [
    ('''
    {
        "employees":[
            {"firstName":"John", "lastName":"Doe"},
            {"firstName":"Anna", "lastName":"Smith"},
            {"firstName":"Peter", "lastName":"Jones"
        ]
    }
    ''',
    '''
    {
        "employees": [
            {"firstName": "John", "lastName": "Doe"},
            {"firstName": "Anna", "lastName": "Smith"},
            {"firstName": "Peter", "lastName": "Jones"}
        ]
    }
    '''),

    ('''
    {
        "name": "Alice",
        "age": "30",
        "city": "New York"
    ''',
    '''
    {
        "name": "Alice",
        "age": "30",
        "city": "New York"
    }
    '''),

    ('''
    {
        "fruit": "apple",
        "size": "large",
        "color": "red",
    }
    ''',
    '''
    {
        "fruit": "apple",
        "size": "large",
        "color": "red"
    }
    '''),

    ('''
    {
        "title": "The Great Gatsby",
        "author": "F. Scott Fitzgerald",
        "published": 1925,
    ''',
    '''
    {
        "title": "The Great Gatsby",
        "author": "F. Scott Fitzgerald",
        "published": 1925
    }
    '''),

    ('''
    {
        "company": "OpenAI",
        "location": "San Francisco"
        "products": ["GPT-3", "Codex", "DALL-E"]
    }
    ''',
    '''
    {
        "company": "OpenAI",
        "location": "San Francisco",
        "products": ["GPT-3", "Codex", "DALL-E"]
    }
    '''),

    ('''
    {
        "movie": "Inception",
        "director": "Christopher Nolan"
        "year": 2010
    }
    ''',
    '''
    {
        "movie": "Inception",
        "director": "Christopher Nolan",
        "year": 2010
    }
    '''),

    ('''
    {
        "car": "Tesla",
        "model": "Model S"
        "year": 2022,
    ''',
    '''
    {
        "car": "Tesla",
        "model": "Model S",
        "year": 2022
    }
    '''),

    ('''
    {
        "country": "Canada",
        "capital": "Ottawa",
        "population": 37.59,
    ''',
    '''
    {
        "country": "Canada",
        "capital": "Ottawa",
        "population": 37.59
    }
    '''),

    ('''
    {
        "book": "To Kill a Mockingbird",
        "author": "Harper Lee",
        "published": "1960"
    ''',
    '''
    {
        "book": "To Kill a Mockingbird",
        "author": "Harper Lee",
        "published": "1960"
    }
    '''),

    ('''
    {
        "device": "iPhone",
        "manufacturer": "Apple",
        "release_year": 2007
    ''',
    '''
    {
        "device": "iPhone",
        "manufacturer": "Apple",
        "release_year": 2007
    }
    ''')
]

# Run the accuracy benchmark for all models
model_accuracies = benchmark_all_models(models, test_cases)

# Plot the accuracies
plot_accuracies(model_accuracies)
