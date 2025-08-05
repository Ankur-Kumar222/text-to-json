# Text-to-JSON CLI Tool

A CLI tool that converts unstructured plain text into a structured JSON format strictly adhering to a specified JSON Schema using OpenAI's Structured Outputs.

## Features
- Converts unstructured text to structured JSON.
- Strict adherence to a given JSON Schema.
- Uses OpenAI's LLM with structured output capabilities.
- CLI-based execution for batch test cases.

---

## Folder Structure
```
text-to-json/
├── main.py
├── .env.example
├── pyproject.toml
├── test-cases/
│   └── test-case-1/
│       └── input/
│           ├── input.json  # JSON Schema file
│           └── input.txt   # Text file to be parsed
│       └── output/
└── README.md
└── documentation
```

---

## Setup Guide

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd text-to-json
```

### 2. Configure Environment Variables
- Copy the example `.env` file and create your own `.env` file:
    ```bash
    cp .env.example .env
    ```
- Open `.env` and fill in the following:
    ```
    OPENAI_API_KEY=your_openai_api_key_here
    LLM_MODEL=any_model_that_supports_structured_outputs
    ```

### 3. Install Dependencies
Ensure you have Python 3.9+ installed.

I use poetry here for package management

---

## Preparing a Test Case Folder

Each test case should follow this structure:

```
test-cases/
└── test-case-n/
    └── input/
        ├── input.json  # JSON Schema file defining expected output structure
        └── input.txt   # Text file to be parsed (e.g., resume, description)
```

- **input.json** → The JSON Schema defining the structure.
- **input.txt** → The raw text content you want to convert.

> Example:
> - `test-cases/test-case-1/input/input.json`
> - `test-cases/test-case-1/input/input.txt`

---

## Running the CLI Tool

Execute the following command to run the parser on a test case:

```bash
python main.py --test-case <path-to-test-case-folder>
```

**Example:**
```bash
python main.py --test-case ./test-cases/test-case-1
```

- The script will look for an `input` folder inside the specified test case folder.
- It will generate the parsed JSON output in an `output` folder within the same test case folder.
- Output file will be named after the input `.txt` file (with `.json` extension).

---

## Example Output

After running, you'll see:
```
Output saved to ./test-cases/test-case-1/output/input.json
```

The output JSON will strictly follow the schema you provided.

---

## How It Works
1. **Reads Input Text & JSON Schema**: From the specified `input` folder.
2. **Sanitizes Schema**: Ensures types, formats, required fields conform to Structured Output requirements.
3. **Calls OpenAI API**: Sends text + schema to OpenAI LLM with Structured Output formatting.
4. **Post-Processes Output**: Cleans up unwanted keys like `$comment`.
5. **Saves Output JSON**: Writes the structured JSON to the `output` directory.

---