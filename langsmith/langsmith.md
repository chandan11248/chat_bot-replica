# LangSmith Usage Guide

## Overview

LangSmith is a powerful platform for debugging, testing, evaluating, and monitoring LLM applications. It provides comprehensive tracing capabilities to help you understand and optimize your AI pipelines.

## Table of Contents

- [Installation](#installation)
- [Basic Setup](#basic-setup)
- [Pipeline Visualization](#pipeline-visualization)
- [Tracing Ordinary Functions](#tracing-ordinary-functions)
- [Advanced Features](#advanced-features)
- [Best Practices](#best-practices)

## Installation

```bash
pip install langsmith langchain
```

## Basic Setup

### Environment Variables

Set up your LangSmith API credentials:

```bash
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_API_KEY=your_api_key_here
export LANGCHAIN_PROJECT=your_project_name
```

Or in Python:

```python
import os

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "your_api_key_here"
os.environ["LANGCHAIN_PROJECT"] = "your_project_name"
```

## Pipeline Visualization

LangSmith automatically traces LangChain operations, providing visual insights into your pipeline execution.

### Example: Simple Chain Visualization

```python
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser

# Create a simple chain
llm = ChatOpenAI(model="gpt-3.5-turbo")
prompt = ChatPromptTemplate.from_template("Tell me a joke about {topic}")
output_parser = StrOutputParser()

chain = prompt | llm | output_parser

# Execute the chain - automatically traced
result = chain.invoke({"topic": "programming"})
print(result)
```

This will automatically appear in your LangSmith dashboard with:
- Input parameters
- Execution time for each component
- Token usage
- Output results
- Complete trace visualization

### Example: Complex Multi-Step Pipeline

```python
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough

llm = ChatOpenAI(model="gpt-3.5-turbo")

# Define multiple prompts
topic_prompt = ChatPromptTemplate.from_template(
    "Generate 3 interesting topics related to: {subject}"
)

essay_prompt = ChatPromptTemplate.from_template(
    "Write a short essay about: {topic}"
)

# Create pipeline
pipeline = (
    {"subject": RunnablePassthrough()}
    | topic_prompt
    | llm
    | {"topic": RunnablePassthrough()}
    | essay_prompt
    | llm
)

# Execute - full pipeline will be visualized
result = pipeline.invoke("artificial intelligence")
```

## Tracing Ordinary Functions

You can trace any Python function using the `@traceable` decorator or the `trace` context manager.

### Method 1: Using `@traceable` Decorator

```python
from langsmith import traceable

@traceable
def fetch_data_from_api(query: str) -> dict:
    """Custom function that will be traced in LangSmith"""
    # Simulate API call
    import time
    time.sleep(0.5)
    return {"data": f"Results for {query}", "count": 10}

@traceable
def process_data(data: dict) -> str:
    """Another traced function"""
    return f"Processed: {data['data']} with {data['count']} items"

@traceable
def complete_workflow(user_query: str) -> str:
    """Main workflow function"""
    raw_data = fetch_data_from_api(user_query)
    processed = process_data(raw_data)
    return processed

# Execute - all functions will be traced
result = complete_workflow("machine learning")
```

### Method 2: Using Context Manager

```python
from langsmith import trace

def regular_function(x: int, y: int) -> int:
    return x + y

# Wrap execution with trace
with trace(name="calculation_workflow", run_type="chain") as rt:
    result1 = regular_function(5, 3)
    rt.metadata = {"step": "addition"}
    
    result2 = regular_function(result1, 10)
    rt.metadata = {"step": "second_addition"}
    
    print(f"Final result: {result2}")
```

### Method 3: Tracing with Custom Metadata

```python
from langsmith import traceable

@traceable(
    name="custom_data_processor",
    metadata={"version": "1.0", "environment": "production"},
    tags=["data-processing", "critical"]
)
def advanced_processor(input_data: list) -> dict:
    """Function with custom trace configuration"""
    processed_items = [item.upper() for item in input_data]
    return {
        "processed": processed_items,
        "count": len(processed_items),
        "status": "success"
    }

# Usage
result = advanced_processor(["apple", "banana", "cherry"])
```

## Advanced Features

### 1. Nested Function Tracing

```python
from langsmith import traceable

@traceable
def validate_input(data: str) -> bool:
    return len(data) > 0 and data.isalnum()

@traceable
def transform_data(data: str) -> str:
    return data.upper()

@traceable
def save_to_database(data: str) -> bool:
    # Simulate database save
    return True

@traceable(name="complete_etl_pipeline")
def etl_pipeline(raw_data: str) -> dict:
    """Nested functions are automatically traced"""
    if not validate_input(raw_data):
        return {"status": "error", "message": "Invalid input"}
    
    transformed = transform_data(raw_data)
    saved = save_to_database(transformed)
    
    return {"status": "success", "data": transformed, "saved": saved}

# All nested function calls will appear in the trace tree
result = etl_pipeline("test_data_123")
```

### 2. Tracing with Error Handling

```python
from langsmith import traceable

@traceable
def risky_operation(value: int) -> int:
    """Function that might fail"""
    if value < 0:
        raise ValueError("Negative values not allowed")
    return value * 2

@traceable
def safe_workflow(value: int) -> dict:
    """Workflow with error handling - errors are captured in traces"""
    try:
        result = risky_operation(value)
        return {"status": "success", "result": result}
    except ValueError as e:
        return {"status": "error", "error": str(e)}

# Both successful and failed executions are traced
safe_workflow(10)  # Success - traced
safe_workflow(-5)  # Error - also traced with error details
```

### 3. Combining LangChain and Custom Functions

```python
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langsmith import traceable

llm = ChatOpenAI(model="gpt-3.5-turbo")

@traceable
def preprocess_query(query: str) -> str:
    """Custom preprocessing step"""
    return query.strip().lower()

@traceable
def postprocess_response(response: str) -> dict:
    """Custom postprocessing step"""
    return {
        "response": response,
        "length": len(response),
        "word_count": len(response.split())
    }

@traceable(name="hybrid_pipeline")
def hybrid_workflow(user_query: str) -> dict:
    """Combines LangChain and custom functions"""
    # Custom preprocessing
    cleaned_query = preprocess_query(user_query)
    
    # LangChain operation
    prompt = ChatPromptTemplate.from_template("Answer briefly: {query}")
    chain = prompt | llm
    llm_response = chain.invoke({"query": cleaned_query})
    
    # Custom postprocessing
    final_result = postprocess_response(llm_response.content)
    
    return final_result

# Complete workflow traced end-to-end
result = hybrid_workflow("  What is Machine Learning?  ")
```

## Best Practices

### 1. Meaningful Names and Metadata

```python
@traceable(
    name="user_authentication_flow",
    metadata={"service": "auth", "version": "2.0"},
    tags=["security", "critical"]
)
def authenticate_user(username: str, token: str) -> bool:
    # Your implementation
    pass
```

### 2. Organize by Projects

```python
import os

# Different projects for different environments
os.environ["LANGCHAIN_PROJECT"] = "production-app"  # For production
os.environ["LANGCHAIN_PROJECT"] = "dev-experiments"  # For development
```

### 3. Selective Tracing

```python
from langsmith import traceable

@traceable
def important_function():
    """This will be traced"""
    helper_function()  # This won't be traced unless decorated

def helper_function():
    """Regular function - not traced"""
    pass
```

### 4. Add Context to Traces

```python
from langsmith import traceable

@traceable
def process_with_context(data: str, user_id: str) -> str:
    """Add relevant context to your traces"""
    # The function parameters automatically become trace inputs
    result = data.upper()
    # Return values automatically become trace outputs
    return result
```

## Use Cases

1. **Debugging**: Identify bottlenecks and errors in your LLM pipeline
2. **Performance Monitoring**: Track latency and token usage across components
3. **Cost Analysis**: Monitor API calls and token consumption
4. **Quality Assurance**: Review and compare outputs across different runs
5. **Collaboration**: Share traces with team members for troubleshooting

## Viewing Traces

After running your code, visit [smith.langchain.com](https://smith.langchain.com) to:

- View detailed trace trees
- Analyze performance metrics
- Compare different runs
- Export data for further analysis
- Set up monitoring and alerts

## Resources

- [Official Documentation](https://docs.smith.langchain.com/)
- [LangSmith Python SDK](https://github.com/langchain-ai/langsmith-sdk)
- [LangChain Documentation](https://python.langchain.com/)

---

*Last Updated: December 2024*