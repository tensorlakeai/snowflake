# Wikipedia Knowledge Base: Tensorlake Extraction + Streamlit Query Interface

This example demonstrates a two-part system that builds and queries an intelligent Wikipedia knowledge base. A Tensorlake application handles extraction and processing, while a Streamlit app provides an interactive query interface.

**NOTE: A full working example is coming soon**

## Overview

This solution consists of two complementary applications:

### 1. `extract-wikipedia.py` - Tensorlake Extraction Application
- Accepts a Wikipedia page type (e.g., "actors", "scientists", "companies")
- Uses **BeautifulSoup** and **Requests** to crawl and fetch HTML from Wikipedia
- Leverages **LangChain + OpenAI** for intelligent HTML parsing, chunking, and extraction:
  - Structured data (dates, locations, career milestones)
  - Key events and biographical summaries
  - Semantic relationships and entities
- Stores everything in **Snowflake**:
  - Structured data tables for facts
  - Text embeddings for semantic search

### 2. `query-wikipedia` - Streamlit Query Application
- Interactive web interface for natural language queries
- Performs **hybrid search** using Snowflake Cortex:
  - Structured data filtering for precise facts
  - Semantic search through embeddings for context
- Generates answers using **OpenAI GPT-4**
- Real-time results with source attribution

## Architecture
```
EXTRACTION (Tensorlake Platform):
Wikipedia Lists → BeautifulSoup (crawl) → Requests (fetch) → LangChain+OpenAI (parse & extract)
→ Snowflake (structured data + embeddings)

QUERY (Streamlit App):
User Interface → Snowflake Cortex (structured query) → Cortex Search (semantic search)
→ OpenAI GPT-4 (answer generation) → Display Results
```

![A diagram outlining the entire pipeline](./Snowflake_Wikipedia_Diagram.png)

## Key Features

### Extraction Application
- **Intelligent Parsing**: LangChain + OpenAI understand HTML structure and extract meaningful information
- **Serverless Execution**: Tensorlake handles scaling, retries, and orchestration automatically
- **Incremental Updates**: Add new Wikipedia categories anytime to expand the knowledge base

### Query Application  
- **Interactive UI**: Streamlit provides a clean, customizable interface
- **Hybrid Search**: Combines SQL queries with vector search for best results
- **Real-time Responses**: Instant answers with source citations
- **Shareable**: Deploy as a web app for your entire team

## Example Queries
```
"What are some key moments in early life that famous movie stars share?"
"Which actors were born in the 1960s and started in theater?"
"Who transitioned from comedy to dramatic roles in their 30s?"
"Find actors with birthdays in December who won Academy Awards"
```

## Getting Started

### Prerequisites

- Tensorlake API key (for the extraction application)
- OpenAI API key (for parsing and generation)
- Snowflake account with Cortex enabled
- Python 3.11+

### Part 1: Deploy Extraction Application

#### 1. Install Tensorlake Dependencies
```bash
pip install --upgrade tensorlake beautifulsoup4 requests langchain openai snowflake-connector-python
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

#### 3. Deploy to Tensorlake Cloud
```bash
tensorlake secrets set OPENAI_API_KEY='YOUR_KEY'
tensorlake secrets set SNOWFLAKE_ACCOUNT='YOUR_ACCOUNT'
tensorlake secrets set SNOWFLAKE_USER='YOUR_SNOWFLAKE_USER'
tensorlake secrets set SNOWFLAKE_PASSWORD='YOUR_SNOWFLAKE_PASSWORD'
tensorlake secrets set SNOWFLAKE_WAREHOUSE='YOUR_SNOWFLAKE_WAREHOUSE'
tensorlake secrets set SNOWFLAKE_DATABASE='YOUR_SNOWFLAKE_DATABASE'
tensorlake secrets set SNOWFLAKE_SCHEMA='YOUR_SNOWFLAKE_SCHEMA'
# ... set other secrets

tensorlake deploy extract-wikipedia.py
```

#### 4. Run Extraction
```bash
# Via API
curl -X POST https://api.tensorlake.ai/applications/extract-wikipedia \
  -H "Authorization: Bearer YOUR_TENSORLAKE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"page_type": "actors", "limit": 100}'

# Or locally
python extract-wikipedia.py --type actors --limit 100
```

### Part 2: Deploy Streamlit Query App

#### 1. Install Streamlit Dependencies
```bash
pip install streamlit snowflake-connector-python openai pandas
```

#### 2. Configure Streamlit Secrets
Create `.streamlit/secrets.toml`:
```toml
[snowflake]
account = "YOUR_ACCOUNT"
user = "YOUR_USER"
password = "YOUR_PASSWORD"
warehouse = "COMPUTE_WH"
database = "WIKIPEDIA_KB"
schema = "ARTICLES"

[openai]
api_key = "YOUR_OPENAI_API_KEY"
```

#### 3. Run Streamlit App
```bash
streamlit run query-wikipedia.py
```

#### 4. Deploy to Streamlit Cloud (Optional)
- Push code to GitHub
- Connect to [Streamlit Cloud](https://streamlit.io/cloud)
- Deploy with your secrets configured

## How It Works

### Extraction Process (Tensorlake)
1. **Discovery**: BeautifulSoup crawls Wikipedia list pages for article URLs
2. **Fetching**: Requests downloads full HTML content
3. **Intelligent Processing**: LangChain + OpenAI parse, chunk, and extract information
4. **Storage**: Snowflake stores structured data and embeddings

### Query Process (Streamlit)
1. **User Input**: Clean web interface for entering queries
2. **Hybrid Search**: Cortex queries structured data then filters semantic search
3. **Context Assembly**: Combines facts and relevant text passages
4. **Answer Generation**: OpenAI GPT-4 creates natural language response
5. **Display**: Results shown with sources and confidence scores

## Customization

### Extending Extraction
- Add new Wikipedia categories in `extract-wikipedia.py`
- Customize LangChain prompts for specific extraction needs
- Adjust chunking strategies for different content types

### Enhancing Query Interface
- Modify Streamlit UI components in `query-wikipedia.py`
- Add filters, charts, or export options
- Customize the display of results and sources

## Files

- `extract-wikipedia.py` - Tensorlake extraction application
- `query-wikipedia.py` - Streamlit query interface
- `requirements.txt` - Python dependencies
- `README.md` - This file