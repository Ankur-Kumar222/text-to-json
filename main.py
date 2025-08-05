import json
import os
import argparse
from openai import OpenAI

OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
LLM_MODEL = os.environ['LLM_MODEL']
client = OpenAI(api_key=OPENAI_API_KEY)

def sanitize_schema_draft_04(schema_part, parent_key=None):
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
            schema_part[key] = sanitize_schema_draft_04(value, parent_key=key)

        if 'properties' in schema_part and 'type' not in schema_part:
            if 'required' not in schema_part:
                schema_part['required'] = list(schema_part['properties'].keys())

    elif isinstance(schema_part, list):
        return [sanitize_schema_draft_04(item, parent_key=parent_key) for item in schema_part]

    return schema_part

def sanitize_schema_draft_07(schema_part, parent_key=None, parent_obj=None):
    """
    Sanitize the JSON schema for draft-07 to ensure it adheres to expected types and formats.
    - Ensures every object with 'properties' has a 'required' array containing all property names.
    - Replaces 'const' with 'enum' and ensures 'type' is present for enums.
    - Removes all 'oneOf' keys, simplifying to the most permissive or first option.
    - Generalizes 'oneOf' simplification logic.
    - Ensures every object schema has 'additionalProperties': false.
    - Removes all properties when '$ref' is present.
    - Removes unsupported formats.
    - Removes 'uniqueItems' from arrays.
    """
    supported_formats = ['date-time', 'time', 'date', 'duration', 'email', 'hostname', 'ipv4', 'ipv6', 'uuid']
    
    if isinstance(schema_part, dict):
        if '$ref' in schema_part:
            ref_value = schema_part['$ref']
            schema_part.clear()
            schema_part['$ref'] = ref_value
            return schema_part
        
        if schema_part.get('type') == 'string' and 'format' in schema_part:
            if schema_part['format'] not in supported_formats:
                del schema_part['format']
        
        if schema_part.get('type') == 'array' and 'uniqueItems' in schema_part:
            del schema_part['uniqueItems']
        
        if schema_part.get('type') == 'object' or 'properties' in schema_part:
            schema_part['additionalProperties'] = False
            if 'properties' in schema_part:
                schema_part['required'] = list(schema_part['properties'].keys())

        if 'const' in schema_part:
            const_value = schema_part.pop('const')
            schema_part['enum'] = [const_value]
            if 'type' not in schema_part:
                schema_part['type'] = 'string'
        if 'enum' in schema_part and 'type' not in schema_part:
            schema_part['type'] = 'string'

        if 'oneOf' in schema_part:
            options = schema_part['oneOf']

            if all(isinstance(opt, dict) and set(opt.keys()) <= {'required'} for opt in options):
                required_keys = set()
                for opt in options:
                    required_keys.update(opt.get('required', []))
                schema_part['required'] = list(required_keys)
                schema_part.pop('oneOf', None)

            elif all(isinstance(opt, dict) and '$ref' in opt for opt in options):
                schema_part.clear()
                schema_part['$ref'] = options[0]['$ref']

            elif all(isinstance(opt, dict) and 'type' in opt for opt in options):
                for k, v in options[0].items():
                    schema_part[k] = v
                schema_part.pop('oneOf', None)

            elif all(isinstance(opt, dict) and set(opt.keys()) <= {'type', 'additionalProperties'} for opt in options):
                for k, v in options[0].items():
                    schema_part[k] = v
                schema_part.pop('oneOf', None)
            else:
                schema_part.pop('oneOf', None)
                schema_part['type'] = 'string'

        for key, value in list(schema_part.items()):
            schema_part[key] = sanitize_schema_draft_07(value, parent_key=key, parent_obj=schema_part)
    elif isinstance(schema_part, list):
        return [sanitize_schema_draft_07(item, parent_key=parent_key, parent_obj=parent_obj) for item in schema_part]
    return schema_part

def detect_schema_version(schema):
    """
    Detect the JSON Schema version from the $schema property.
    Returns 'draft-04' or 'draft-07' or 'unknown'.
    """
    schema_url = schema.get('$schema', '')
    if 'draft-04' in schema_url:
        return 'draft-04'
    elif 'draft-07' in schema_url:
        return 'draft-07'
    else:
        return 'unknown'

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
        input_text = f.read()

    with open(schema_file, 'r') as f:
        schema = json.load(f)

    schema_version = detect_schema_version(schema)
    
    if schema_version == 'draft-04':
        schema = sanitize_schema_draft_04(schema)
    elif schema_version == 'draft-07':
        schema = sanitize_schema_draft_07(schema)
    else:
        print(f"Warning: Unknown schema version, defaulting to draft-04 sanitization")
        schema = sanitize_schema_draft_04(schema)

    response = client.responses.create(
        model=LLM_MODEL,
        input=[
            {"role": "system", "content": "You are a helpful assistant for parsing and structuring textual data according to a JSON schema."},
            {"role": "user", "content": f"Convert this text to the specified JSON schema format:\n\n{input_text}"}
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
    parser = argparse.ArgumentParser(description="Text-to-JSON Parser CLI")
    parser.add_argument('--test-case', required=True, help='Path to the test-case-n folder')

    args = parser.parse_args()
    process_test_case(args.test_case)
