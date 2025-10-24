# Wikipedia Knowledge Base with Tensorlake + Snowflake + OpenAI

This example demonstrates how to build an intelligent Q&A system that uses Tensorlake's data processing capabilities to parse and chunk Wikipedia articles, stores them in Snowflake with Cortex Search, and generates answers using OpenAI's GPT-4.

**NOTE: A full working example is coming soon**

## Overview

This Tensorlake application showcases a complete RAG pipeline with best-in-class tools:

1. **`query-wikipedia.py`** - Intelligent Wikipedia knowledge base that:
   - Uses OpenAI GPT-4 to identify the most relevant Wikipedia article
   - Fetches articles and uses **Tensorlake DocumentAI** for intelligent parsing and chunking
   - Stores structured chunks in Snowflake with metadata
   - Performs retrieval using **Snowflake Cortex Search** (with fallback options)
   - Generates accurate answers using **OpenAI GPT-4** with retrieved context

## Architecture

- **Article Selection**: OpenAI identifies the best Wikipedia article for any query
- **Document Processing**: Tensorlake DocumentAI handles parsing and chunking
- **Storage & Search**: Snowflake stores chunks with Cortex Search for intelligent retrieval
- **Answer Generation**: OpenAI GPT-4 generates contextual answers from retrieved chunks
- **Persistent Knowledge**: Each query enriches your searchable knowledge base

## How It Works
```
User Query → OpenAI (topic extraction) → Wikipedia API → Tensorlake (parsing & chunking) 
→ Snowflake (storage) → Cortex Search (retrieval) → OpenAI (answer generation) → Response
```

![A diagram outlining the entire pipeline of the APplication](./Snowflake_Wikipedia_Diagram.png)

## Example Queries

- "How do snowflakes form in the atmosphere?"
- "What causes volcanic eruptions?"
- "Explain quantum entanglement"
- "How does photosynthesis work in plants?"

## Getting Started

### Prerequisites

- Tensorlake API key (for document processing)
- OpenAI API key (for LLM capabilities)
- Snowflake account with credentials
- Python 3.11+

### Local Testing

#### 1. Install Dependencies
```bash
pip install --upgrade tensorlake snowflake-connector-python wikipedia openai
```

#### 2. Set Environment Variables
```bash
export TENSORLAKE_API_KEY=YOUR_TENSORLAKE_API_KEY
export OPENAI_API_KEY=YOUR_OPENAI_API_KEY
export SNOWFLAKE_ACCOUNT=YOUR_SNOWFLAKE_ACCOUNT
export SNOWFLAKE_USER=YOUR_SNOWFLAKE_USER
export SNOWFLAKE_PASSWORD=YOUR_SNOWFLAKE_PASSWORD
export SNOWFLAKE_WAREHOUSE=COMPUTE_WH
export SNOWFLAKE_DATABASE=WIKIPEDIA_KB
export SNOWFLAKE_SCHEMA=ARTICLES
```

#### 3. Run a Query
```bash
python query-wikipedia.py
```

### Deploying to Tensorlake Cloud

#### 1. Set Secrets
```bash
tensorlake secrets set TENSORLAKE_API_KEY='YOUR_TENSORLAKE_API_KEY'
tensorlake secrets set OPENAI_API_KEY='YOUR_OPENAI_API_KEY'
tensorlake secrets set SNOWFLAKE_ACCOUNT='YOUR_SNOWFLAKE_ACCOUNT'
tensorlake secrets set SNOWFLAKE_USER='YOUR_SNOWFLAKE_USER'  
tensorlake secrets set SNOWFLAKE_PASSWORD='YOUR_SNOWFLAKE_PASSWORD'
tensorlake secrets set SNOWFLAKE_WAREHOUSE='COMPUTE_WH'
tensorlake secrets set SNOWFLAKE_DATABASE='WIKIPEDIA_KB'
tensorlake secrets set SNOWFLAKE_SCHEMA='ARTICLES'
```

#### 2. Deploy Application
```bash
tensorlake deploy query-wikipedia.py
```

#### 3. Query via API
```bash
curl -X POST https://api.tensorlake.ai/applications/query-wikipedia \
  -H "Authorization: Bearer YOUR_TENSORLAKE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "How do snowflakes form?"}'
```

## Key Features

- **Intelligent Document Processing**: Tensorlake DocumentAI provides superior parsing that preserves semantic meaning
- **Flexible Search**: Automatically uses Cortex Search when available, falls back to text search
- **Growing Knowledge Base**: Each query adds to your persistent Wikipedia knowledge base
- **Production Ready**: Handles errors gracefully with multiple fallback strategies

## Files

- `query-wikipedia.py` - Main application orchestrating the entire pipeline
- `README.md` - This file