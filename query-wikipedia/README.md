# Wikipedia Knowledge Base with Snowflake Integration

This example demonstrates how to build an intelligent Q&A system that fetches Wikipedia articles, chunks them semantically, stores them in Snowflake, and answers questions using RAG (Retrieval-Augmented Generation).

**NOTE: This example is coming soon**

## Overview

This Tensorlake Application showcases a complete knowledge base pipeline:

1. **`query-wikipedia.py`** - Intelligent Wikipedia article fetcher and Q&A system that:
   - Uses AI to identify the most relevant Wikipedia article for any query
   - Fetches and chunks articles into semantic segments
   - Stores content in Snowflake with optional vector embeddings
   - Performs intelligent retrieval using multiple search strategies
   - Generates accurate answers using RAG with OpenAI

## How It Works

Ask any question → AI finds the right Wikipedia article → Content is chunked and stored → Semantic search finds relevant sections → AI generates an answer from the context

![Diagram of the Tensorlake Application that stores wikipedia pages in Snowflake for NLP querying with OpenAI.](./Snowflake_Wikipedia_Diagram.png)

## Example Queries

- "How do snowflakes form in the atmosphere?"
- "What causes volcanic eruptions?"
- "How does photosynthesis work?"
- "What is quantum entanglement?"

## Getting Started

### Prerequisites

- Tensorlake API key
- Snowflake account with credentials
- OpenAI API key for LLM capabilities
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

Or modify the query in the script:
```python
query = "Your question here"
```

### Deploying to Tensorlake Cloud

#### 1. Set Secrets
```bash
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

## Architecture

- **Intelligent Article Selection**: Uses LLM to map queries to Wikipedia topics
- **Semantic Chunking**: Splits articles preserving paragraph boundaries
- **Multi-Strategy Search**: Falls back gracefully from vector → semantic → keyword search
- **Snowflake Storage**: Persistent knowledge base that grows with each query
- **RAG Generation**: Combines retrieved context with LLM for accurate answers

## Files

- `query-wikipedia.py` - Main application that fetches, stores, and queries Wikipedia content
- `README.md` - This file