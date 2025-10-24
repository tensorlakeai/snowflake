# Document Q&A with Snowflake Cortex + OpenAI

This example demonstrates a document Q&A system that accepts any document URL, uses Snowflake Cortex to parse and chunk it, performs intelligent search with Cortex Search, and generates answers using OpenAI.

**NOTE: A full working example is coming soon**

## Overview

This Tensorlake application showcases Snowflake Cortex's complete document processing capabilities:

1. **`document-qa.py`** - Document processing and Q&A system that:
   - Accepts any document URL (PDFs, web pages, text files)
   - Uses **Snowflake Cortex PARSE_DOCUMENT** for document parsing
   - Chunks content using **Snowflake Cortex text splitting functions**
   - Indexes chunks with **Snowflake Cortex Search** for hybrid retrieval
   - Generates precise answers using **OpenAI GPT-4** with retrieved context

## Architecture
```
Document URL → Fetch → Snowflake Cortex (parse & chunk) → Cortex Search (index)
User Query → Cortex Search (retrieve) → OpenAI GPT-4 (generate) → Answer
```

![A diagram of the pipeline for this Application](./Snowflake_DocQA_Diagram.png)

## Key Features

- **Native Snowflake Processing**: All document processing happens within Snowflake
- **Cortex Document Parser**: Handles PDFs, text, and various document formats
- **Intelligent Chunking**: Cortex text splitting preserves semantic boundaries
- **Hybrid Search**: Cortex Search combines keyword and semantic retrieval
- **Contextual Answers**: OpenAI generates answers grounded in document content
- **Unified Platform**: Minimal data movement - everything stays in Snowflake

## Example Usage

Process documents and ask questions:
```python
# Process a PDF document
document_url = "https://www.sec.gov/Archives/edgar/data/1318605/000095017022000796/tsla-20211231.pdf"
query = "What are the main risk factors?"

# Process a web page
document_url = "https://docs.snowflake.com/en/user-guide/cortex-search"
query = "How does hybrid search work?"

# Process a text document
document_url = "https://raw.githubusercontent.com/example/repo/main/README.md"
query = "What are the installation steps?"
```

## Getting Started

### Prerequisites

- Tensorlake API key (for orchestration)
- Snowflake account with Cortex features enabled
- OpenAI API key (for answer generation)
- Python 3.11+

### Snowflake Setup

Ensure your Snowflake account has:
- Cortex AI features enabled
- Access to `SNOWFLAKE.CORTEX.PARSE_DOCUMENT`
- Access to `SNOWFLAKE.CORTEX.SPLIT_TEXT_RECURSIVE_CHARACTER`
- Cortex Search Service capabilities

### Local Testing

#### 1. Install Dependencies
```bash
pip install --upgrade tensorlake snowflake-connector-python openai requests
```

#### 2. Set Environment Variables
```bash
export TENSORLAKE_API_KEY=YOUR_TENSORLAKE_API_KEY
export OPENAI_API_KEY=YOUR_OPENAI_API_KEY
export SNOWFLAKE_ACCOUNT=YOUR_SNOWFLAKE_ACCOUNT
export SNOWFLAKE_USER=YOUR_SNOWFLAKE_USER
export SNOWFLAKE_PASSWORD=YOUR_SNOWFLAKE_PASSWORD
export SNOWFLAKE_WAREHOUSE=COMPUTE_WH
export SNOWFLAKE_DATABASE=DOCUMENT_QA
export SNOWFLAKE_SCHEMA=CORTEX_DOCS
```

#### 3. Run Document Q&A
```bash
python document-qa.py --url "https://example.com/document.pdf" --query "Your question here"
```

### Deploying to Tensorlake Cloud

#### 1. Set Secrets
```bash
tensorlake secrets set TENSORLAKE_API_KEY='YOUR_KEY'
tensorlake secrets set OPENAI_API_KEY='YOUR_KEY'
tensorlake secrets set SNOWFLAKE_ACCOUNT='YOUR_ACCOUNT'
tensorlake secrets set SNOWFLAKE_USER='YOUR_USER'
tensorlake secrets set SNOWFLAKE_PASSWORD='YOUR_PASSWORD'
tensorlake secrets set SNOWFLAKE_WAREHOUSE='COMPUTE_WH'
tensorlake secrets set SNOWFLAKE_DATABASE='DOCUMENT_QA'
tensorlake secrets set SNOWFLAKE_SCHEMA='CORTEX_DOCS'
```

#### 2. Deploy Application
```bash
tensorlake deploy document-qa.py
```

#### 3. Query via API
```bash
curl -X POST https://api.tensorlake.ai/applications/document-qa \
  -H "Authorization: Bearer YOUR_TENSORLAKE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "document_url": "https://example.com/document.pdf",
    "query": "What are the key findings?"
  }'
```

## How It Works

1. **Document Fetching**: Application fetches document from URL
2. **Cortex Parsing**: `PARSE_DOCUMENT` extracts text and structure
3. **Cortex Chunking**: `SPLIT_TEXT_RECURSIVE_CHARACTER` creates semantic chunks
4. **Storage & Indexing**: Chunks stored and indexed with Cortex Search
5. **Query Processing**: Cortex Search finds relevant chunks
6. **Answer Generation**: OpenAI GPT-4 synthesizes answer from context

## Supported Document Types

Via Snowflake Cortex:
- **PDFs**: Including complex layouts and tables
- **Text Files**: Plain text, markdown, CSV
- **Office Documents**: When supported by Cortex
- **Web Pages**: HTML content (fetched as text)

## Files

- `document-qa.py` - Main application for document Q&A
- `README.md` - This file