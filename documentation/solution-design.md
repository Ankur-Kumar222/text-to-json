# Text-to-JSON Parser Solution Design Document

## Overview

This solution implements a robust text-to-JSON conversion system that transforms unstructured plain text into structured JSON format while strictly adhering to provided JSON schemas. The system leverages OpenAI's structured output capabilities to ensure schema compliance and includes comprehensive schema sanitization for compatibility across different JSON Schema draft versions.

## Architecture & Core Components

### 1. System Architecture
```
Input Text + JSON Schema → Schema Sanitization → LLM Processing → JSON Output
```

The system follows a pipeline approach:
- **Input Processing**: Reads text files and JSON schema files from designated directories
- **Schema Sanitization**: Normalizes schemas to ensure compatibility with OpenAI's structured output requirements
- **LLM Processing**: Uses OpenAI's API with structured output to convert text to JSON
- **Output Generation**: Produces clean, schema-compliant JSON files

### 2. Core Components

#### Schema Sanitization Engine
The system includes two specialized schema sanitizers to handle different JSON Schema draft versions:

**Draft-04 Sanitizer (`sanitize_schema_draft_04`)**:
- Enforces supported data types (`string`, `number`, `boolean`, `integer`, `object`, `array`)
- Validates and filters supported formats (date-time, email, UUID, etc.)
- Sets `additionalProperties: false` for strict object validation
- Auto-generates `required` arrays from object properties
- Recursively processes nested structures

**Draft-07 Sanitizer (`sanitize_schema_draft_07`)**:
- Handles advanced Draft-07 features like `oneOf`, `const`, and `$ref`
- Converts `const` values to `enum` arrays for compatibility
- Simplifies complex `oneOf` constructs using intelligent heuristics
- Removes unsupported array properties like `uniqueItems`
- Preserves `$ref` references while cleaning other properties

#### Schema Version Detection
Automatic detection of JSON Schema versions based on the `$schema` property, enabling appropriate sanitization strategy selection.

#### Output Sanitization
Removes internal schema properties (keys starting with `$`) from the final output to ensure clean, production-ready JSON.

## Technical Implementation Details

### LLM Integration
- **Model Flexibility**: gpt-4.1-nano
- **Structured Output**: Leverages OpenAI's `responses.create` API with strict JSON schema enforcement
- **Temperature Control**: Set to 0

### File Processing Pipeline
1. **Directory Structure**: Expects `input/` folder with `.txt` and `.json` files
2. **Automatic File Detection**: Dynamically identifies text and schema files
3. **Output Management**: Creates `output/` directory and generates appropriately named JSON files

## CLI Interface

### Command Structure
```bash
python script.py --test-case /path/to/test-case-folder
```

### Directory Convention
```
test-case-n/
├── input/
│   ├── data.txt
│   └── schema.json
└── output/
    └── data.json (generated)
```

## Conclusion

This solution represents a good attempt at building a text-to-JSON conversion system with strong architectural foundations, featuring dual sanitization for schema compatibility. While the modular design and clear separation of concerns provide an excellent foundation for future development, the current implementation did not pass all test cases and requires further refinement in areas such as edge case handling, schema interpretation accuracy, and output validation to achieve production ready reliability.