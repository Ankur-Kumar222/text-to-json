# AI Solution Design: Unstructured Text to JSON Schema Conversion

## Goal
Design and prototype a system which converts unstructured plain text into structured format strictly following a desired JSON schema.

## Problem Statement
The challenge lies in transforming unstructured text data into a well-defined schema format - a classic problem in data engineering and AI. The primary complexity arises from ensuring the output strictly adheres to the provided JSON schema while maintaining semantic accuracy.

## Solution Overview

### Alternative Approaches Considered

#### Fine-Tuned Models: NuExtract
Before settling on OpenAI's structured outputs, I evaluated **NuExtract** - a specialized fine-tuned model designed specifically for structured data extraction tasks.

**Advantages of NuExtract:**
- Superior performance compared to frontier models for extraction tasks
- Purpose built for converting unstructured text to structured formats
- Potentially better accuracy for complex schema adherence

**Why I Didn't Choose NuExtract:**
- More difficult to configure and deploy compared to API-based solutions
- Would require additional setup time and infrastructure considerations
- OpenAI's API provided faster prototyping and iteration cycles

### Selected Approach: Structured Outputs with JSON Schema Mode
Given the project constraints and timeline, I chose OpenAI's structured output capabilities as the most practical solution. The implementation involved:

- **Input**: Unstructured text and target JSON schema
- **Processing**: OpenAI API with structured output mode
- **Output**: Structured data conforming to the schema
- **Configuration**: Temperature set to 0 to minimize hallucinations

### Key Technical Challenge: JSON Schema Version Compatibility

#### The Problem
OpenAI's structured output feature only supports a specific subset of JSON Schema rules, based on the **2020-12 version (Draft 8 patch 1)**. However, the test cases used older schema versions:
- Draft-04 schemas
- Draft-07 schemas

This version mismatch created immediate compatibility issues when attempting to use schemas directly with the OpenAI API.

#### Research Findings
- **OpenAI Documentation**: [Structured Outputs Guide](https://platform.openai.com/docs/guides/structured-outputs)
- **Schema Version**: OpenAI adopts JSON Schema 2020-12 (Draft 8 patch 1)
- **Community Discussion**: [JSON Schema Version Requirements](https://community.openai.com/t/whitch-json-schema-version-should-function-calling-use/283535)

### Implementation Strategy

#### Phase 1: Manual Schema Conversion (Draft-04 to OpenAI Format)
Since no existing conversion libraries provided reliable solutions, I developed a custom conversion function:

- **Approach**: Manual observation of schema differences between Draft-04 and OpenAI format
- **Implementation**: Custom conversion function handling the structural differences
- **Result**: **Test Case 3 passed** with good output generation
- **Tool Enhancement**: Converted the solution into a CLI tool for easier runtime execution

#### Phase 2: Draft-07 Schema Handling
Extended the conversion approach to handle Draft-07 schemas:

- **Result**: **Test Case 1 partially passed** - schema successfully sanitized
- **Limitation**: **Test Case 2 failed** - schema conversion errors persisted
- **Analysis**: Additional edge cases require more comprehensive handling

#### Phase 3: LLM-Assisted Schema Alignment (Experimental)
Developed an alternative approach using LLM assistance:

- **Method**: Used an LLM to align arbitrary JSON schemas to OpenAI's format
- **Input**: Original schema + comprehensive rules document for OpenAI schema requirements
- **Rationale**: Leveraging AI's pattern recognition for complex schema transformations
- **Status**: Proof of concept - requires refinement for production use

## OpenAI Structured Output Constraints

### Supported Schema Features
#### Data Types
- String, Number, Boolean, Integer
- Object, Array, Enum
- anyOf (with restrictions)

#### String Properties
- `pattern` - Regular expression validation
- `format` - Predefined formats:
  - date-time, time, date, duration
  - email, hostname, ipv4, ipv6, uuid

#### Numeric Properties
- `multipleOf`, `maximum`, `exclusiveMaximum`
- `minimum`, `exclusiveMinimum`

#### Array Properties
- `minItems`, `maxItems`

### Critical Limitations
1. **Root Object Constraint**: Must be an object, cannot be `anyOf`
2. **Required Fields**: All fields must be marked as required
3. **Nesting Limits**: Maximum 5 levels of nesting, 5000 object properties total
4. **String Size Limits**: 120,000 character limit for all property names, definitions, enum values
5. **Enum Constraints**: Maximum 1000 enum values, 15,000 characters for large enums
6. **Additional Properties**: Must set `additionalProperties: false`
7. **Unsupported Features**: `allOf`, `not`, `dependentRequired`, `dependentSchemas`, `if/then/else`

## Results Analysis

### Test Case Performance
| Test Case | Schema Version | Status | Notes |
|-----------|---------------|---------|--------|
| Test Case 1 | Draft-07 |  Partially Passed | Schema successfully sanitized but schema too large |
| Test Case 2 | Draft-07 |  Failed | Schema sanitization errors |
| Test Case 3 | Draft-04 |  Passed | Good output quality with manual conversion |

### Output Quality Observations
- **Test Case 3**: Decent output quality using GPT-4.1-nano
- **Test Case 1**: Schema too large, LLM struggled with complete accuracy
- **Model Consideration**: Larger models could improve output field quality

## Trade-offs and Limitations

### Current Limitations
1. **Schema Coverage**: Incomplete handling of all Draft-07 edge cases
2. **Model Size**: Using GPT-4.1-nano may limit output quality for complex schemas
3. **Manual Conversion**: Requires custom logic for each schema version
4. **Large Schema Handling**: Performance degrades with very large schema definitions

### Design Trade-offs
- Chose strict OpenAI compliance over broad schema support
- Prioritized working solution over comprehensive edge case handling
- Used smaller model to balance performance and resource usage

## Future Improvements

### With More Time and Compute
1. **Enhanced Schema Understanding**
   - Deeper study of JSON Schema specifications across versions
   - Comprehensive analysis of OpenAI's schema parsing mechanisms

2. **Universal Schema Converter**
   - Develop holistic conversion function supporting all schema versions
   - Leverage LLMs for intelligent schema transformation
   - Implement automated validation and correction mechanisms

3. **Quality Assurance Pipeline**
   - Automated schema validation testing
   - Output quality metrics and optimization
   - Comprehensive test suite across schema variations

4. **Performance Optimization**
   - Support for large context windows (50k+ text inputs, 100k+ schema files)
   - Handling of deeply nested schemas (7+ levels)
   - Efficient processing of schemas with 1k+ literals

## Conclusion

The solution successfully demonstrates the feasibility of converting unstructured text to structured JSON using AI-powered approaches. While the current implementation handles core use cases effectively, the primary challenge remains in creating a robust, universal schema conversion system that can handle the full spectrum of JSON Schema versions and edge cases.

The hybrid approach of manual conversion combined with LLM assistance shows promise and could be the foundation for a more comprehensive solution given additional development time and computational resources.

---