# Wikipedia Knowledge Base with Tensorlake + Snowflake + OpenAI

This example demonstrates a two-application system that builds and queries an intelligent Wikipedia knowledge base. The first app extracts structured data and summaries from Wikipedia pages, while the second provides natural language Q&A using hybrid search.

**NOTE: A full working example is coming soon**

## Overview

This Tensorlake solution consists of two complementary applications:

### 1. `extract-wikipedia.py` - Knowledge Base Builder
- Accepts a Wikipedia page type (e.g., "actors", "scientists", "companies")
- Uses **BeautifulSoup** and **Requests** to crawl and fetch HTML from relevant Wikipedia pages
- Leverages **Tensorlake DocumentAI** to parse HTML and extract:
  - Structured data (dates, locations, career milestones)
  - Key events and summaries
  - Biographical or historical information
- Stores everything in Snowflake with:
  - Structured data tables for factual information
  - Text embeddings for semantic search

### 2. `query-wikipedia.py` - Intelligent Q&A System
- Accepts natural language queries
- Performs **hybrid search** using Snowflake Cortex:
  - First: Queries structured data for factual filtering
  - Then: Uses results to refine semantic search through embeddings
- Generates contextual answers using **OpenAI GPT-4**

## Architecture
```
EXTRACTION PIPELINE:
Wikipedia Lists → BeautifulSoup (crawl) → Requests (fetch HTML) → Tensorlake (parse & extract)
→ Snowflake (structured data + embeddings)

QUERY PIPELINE:
User Query → Snowflake Cortex (structured query) → Cortex Search (filtered semantic search)
→ OpenAI GPT-4 (answer generation) → Response
```

![A diagram outlining the entire pipeline of the Application](./Snowflake_Wikipedia_Diagram.png)

## Example Usage

### Building the Knowledge Base
```python
# Extract all actors' information
extract_wikipedia("actors")

# Extract scientists' data
extract_wikipedia("scientists")

# Extract companies' information
extract_wikipedia("companies")
```

### Querying the Knowledge Base
```python
# Query examples
"What are some key moments in early life that famous movie stars share?"
"Which actors were born in the 1960s and started in theater?"
"Who transitioned from comedy to dramatic roles in their 30s?"
"What actors have birthdays in December?"
```

## Key Features

- **Intelligent Extraction**: Tensorlake DocumentAI understands HTML structure and extracts both facts and narratives
- **Hybrid Search**: Combines structured queries with semantic search for superior relevance
- **Incremental Building**: Add new Wikipedia categories anytime to expand your knowledge base
- **Production Ready**: Handles pagination, rate limiting, and errors gracefully

## Getting Started

### Prerequisites

- Tensorlake API key (for HTML parsing and extraction)
- OpenAI API key (for answer generation)
- Snowflake account with Cortex enabled
- Python 3.11+

### Local Testing

#### 1. Install Dependencies
```bash
pip install --upgrade tensorlake snowflake-connector-python openai beautifulsoup4 requests
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

#### 3. Build Knowledge Base
```bash
# Extract actor data
python extract-wikipedia.py --type actors --limit 100
```

#### 4. Query the System
```bash
python query-wikipedia.py --query "Which actors born in the 1980s won Academy Awards?"
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

#### 2. Deploy Applications
```bash
tensorlake deploy extract-wikipedia.py
tensorlake deploy query-wikipedia.py
```

#### 3. Use via API

Extract Wikipedia data:
```bash
curl -X POST https://api.tensorlake.ai/applications/extract-wikipedia \
  -H "Authorization: Bearer YOUR_TENSORLAKE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"page_type": "actors", "limit": 50}'
```

Query the knowledge base:
```bash
curl -X POST https://api.tensorlake.ai/applications/query-wikipedia \
  -H "Authorization: Bearer YOUR_TENSORLAKE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "What early life experiences do famous actors share?"}'
```

## How It Works

### Extraction Process
1. **Page Discovery**: BeautifulSoup crawls Wikipedia list pages to find individual article URLs
2. **HTML Fetching**: Requests library downloads full HTML content
3. **Intelligent Parsing**: Tensorlake DocumentAI extracts structured data and summaries
4. **Dual Storage**: Snowflake stores both structured facts and searchable text embeddings

### Query Process
1. **Structured Filtering**: Cortex first queries factual data (dates, locations, categories)
2. **Semantic Search**: Uses structured results to filter embedding search for relevant text
3. **Context Retrieval**: Combines factual and semantic results for comprehensive context
4. **Answer Generation**: OpenAI GPT-4 synthesizes natural language response

## Files

- `extract-wikipedia.py` - Extraction application for building knowledge base
- `query-wikipedia.py` - Query application for Q&A
- `README.md` - This file