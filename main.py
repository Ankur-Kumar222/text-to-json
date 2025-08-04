import json
from openai import OpenAI
import os

OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
LLM_MODEL = os.environ['LLM_MODEL']

client = OpenAI(api_key=OPENAI_API_KEY)

def sanitize_schema(schema_part, parent_key=None):
    """
    Recursively sanitize the schema to ensure all types are supported by Structured Outputs.
    Convert unsupported types to 'string'.
    Handles cases where 'type' is both a schema keyword and a property name.
    Adds required arrays for all objects with properties.
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

def remove_dollar_properties(obj):
    """
    Recursively remove properties that start with '$' from a dictionary or list.
    """
    if isinstance(obj, dict):
        return {k: remove_dollar_properties(v) for k, v in obj.items() if not k.startswith('$')}
    elif isinstance(obj, list):
        return [remove_dollar_properties(item) for item in obj]
    else:
        return obj

resume_path = "/Users/ankur/Desktop/text-to-json/test-cases/test-case-3/Ankur_Resume.txt"

schema_path = "/Users/ankur/Desktop/text-to-json/test-cases/test-case-3/convert your resume to this schema.json"

with open(resume_path, 'r', encoding='utf-8') as file:
    resume_text = file.read()

with open(schema_path, 'r') as schema_file:
    schema = json.load(schema_file)

schema = sanitize_schema(schema)

response = client.responses.create(
    model=LLM_MODEL,
    input=[
        {"role": "system", "content": "You are a helpful assistant for parsing and structuring resume data according to a JSON schema."},
        {"role": "user", "content": f"Convert this resume text to the specified JSON schema format:\n\n{resume_text}"}
    ],
    text={
        "format": {
            "type": "json_schema",
            "name": "resume",
            "schema": schema,
            "strict": True
        }
    },
    temperature=0
)

parsed_json = json.loads(response.output_text)
cleaned_json = remove_dollar_properties(parsed_json)
cleaned_json_string = json.dumps(cleaned_json, indent=2, ensure_ascii=False)

with open("/Users/ankur/Desktop/text-to-json/test-cases/test-case-3/Ankur_Resume.json", "w", encoding="utf-8") as output_file:
    output_file.write(cleaned_json_string)