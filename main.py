import json
import os
import argparse
from openai import OpenAI

OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
LLM_MODEL = os.environ['LLM_MODEL']
client = OpenAI(api_key=OPENAI_API_KEY)

def sanitize_schema(schema_part, parent_key=None):
    """
    Sanitize the JSON schema to ensure it adheres to expected types and formats.
    This function modifies the schema in place, ensuring that:
    - Unsupported types are set to 'string'.
    - Unsupported formats are removed.
    - Additional properties are set to false.
    - Required properties are set based on the presence of 'properties'.
    - Recursively processes nested objects and arrays.
    """

    supported_types = ['string', 'number', 'boolean', 'integer', 'object', 'array']
    supported_formats = ['date-time', 'time', 'date', 'duration', 'email', 'hostname', 'ipv4', 'ipv6', 'uuid']

    if isinstance(schema_part, dict):
        if parent_key != 'properties' and 'type' in schema_part:
            if schema_part['type'] not in supported_types:
                schema_part['type'] = 'string'

        if schema_part.get('type') == 'string' and 'format' in schema_part:
            if schema_part['format'] not in supported_formats:
                del schema_part['format']

        if 'additionalProperties' in schema_part:
            schema_part['additionalProperties'] = False

        if schema_part.get('type') == 'object' and 'properties' in schema_part:
            if 'required' not in schema_part:
                schema_part['required'] = list(schema_part['properties'].keys())

        for key, value in list(schema_part.items()):
            schema_part[key] = sanitize_schema(value, parent_key=key)

        if 'properties' in schema_part and 'type' not in schema_part:
            if 'required' not in schema_part:
                schema_part['required'] = list(schema_part['properties'].keys())

    elif isinstance(schema_part, list):
        return [sanitize_schema(item, parent_key=parent_key) for item in schema_part]

    return schema_part

def sanitize_output(obj):
    """
    Sanitize the output JSON to remove any keys that start with '$'.
    """

    if isinstance(obj, dict):
        return {k: sanitize_output(v) for k, v in obj.items() if not k.startswith('$')}
    elif isinstance(obj, list):
        return [sanitize_output(item) for item in obj]
    else:
        return obj

def process_test_case(test_case_path):
    """
    Process a test case by reading the text and schema from files,
    parsing the text into JSON format according to the schema,
    and saving the output to a JSON file.
    """

    input_dir = os.path.join(test_case_path, "input")
    output_dir = os.path.join(test_case_path, "output")
    os.makedirs(output_dir, exist_ok=True)

    txt_file = None
    schema_file = None
    for file_name in os.listdir(input_dir):
        if file_name.lower().endswith('.txt'):
            txt_file = os.path.join(input_dir, file_name)
        elif file_name.lower().endswith('.json'):
            schema_file = os.path.join(input_dir, file_name)

    if not txt_file or not schema_file:
        print("Error: Could not find both .txt and .json schema files in 'input' folder.")
        return

    with open(txt_file, 'r', encoding='utf-8') as f:
        resume_text = f.read()

    with open(schema_file, 'r') as f:
        schema = json.load(f)

    schema = sanitize_schema(schema)

    response = client.responses.create(
        model=LLM_MODEL,
        input=[
            {"role": "system", "content": "You are a helpful assistant for parsing and structuring textual data according to a JSON schema."},
            {"role": "user", "content": f"Convert this text to the specified JSON schema format:\n\n{resume_text}"}
        ],
        text={
            "format": {
                "type": "json_schema",
                "name": "text-to-json",
                "schema": schema,
                "strict": True
            }
        },
        temperature=0
    )

    parsed_json = json.loads(response.output_text)
    cleaned_json = sanitize_output(parsed_json)
    cleaned_json_string = json.dumps(cleaned_json, indent=2, ensure_ascii=False)

    output_file_path = os.path.join(output_dir, os.path.basename(txt_file).replace('.txt', '.json'))
    with open(output_file_path, "w", encoding="utf-8") as f:
        f.write(cleaned_json_string)

    print(f"Output saved to {output_file_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Resume Text-to-JSON Parser CLI")
    parser.add_argument('--test-case', required=True, help='Path to the test-case-n folder')

    args = parser.parse_args()
    process_test_case(args.test_case)
