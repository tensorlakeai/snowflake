# SEC Filings AI Risk Analysis Example

This example demonstrates how to use Tensorlake Applications to extract and analyze AI-related risk mentions from SEC filings.

## Overview

This example contains two Tensorlake applications:

1. **`process-sec.py`** - Extracts AI risk data from SEC filings using Tensorlake DocAI and stores it in Snowflake
2. **`query-sec.py`** - Queries the extracted data with 6 pre-defined analysis options

The example processes 10 SEC filings across 4 companies to identify and categorize AI-related risks.

You can try this example out using [this Colab Notebook](https://tlake.link/notebooks/snowflake-applications) as well, just make sure to add the two files (`process-sec.py` and `query-sec.py`) to your Notebook environment before starting.

## Available Queries

- `0` - Risk category distribution
- `1` - Operational AI risks
- `2` - Emerging risks in 2025
- `3` - Risk timeline analysis
- `4` - Company risk profiles
- `5` - Company summary statistics

## Getting Started

### Prerequisites

- Tensorlake API key
- Snowflake account with appropriate credentials
- Python 3.11+

### Snowflake Setup

This example requires a Snowflake account with:

1. **A warehouse** for compute (e.g., `COMPUTE_WH`)
2. **A database and schema** for storing the extracted data (we will set this up)

The application will automatically create the following tables in your specified database/schema:

- `AI_RISK_FILINGS` - Main table containing filing metadata and AI risk indicators
- `AI_RISK_MENTIONS` - Detailed table of individual AI risk mentions with categories and descriptions

If you don't have a Snowflake account, you can:
- Sign up for a [free trial](https://signup.snowflake.com/)
- Use the default `COMPUTE_WH` warehouse
- Find your account identifier, username, and password

### Local Testing

#### 1. Install Dependencies

```bash
pip install --upgrade tensorlake snowflake-connector-python pandas pyarrow
```

#### 2. Set Environment Variables

```bash
export TENSORLAKE_API_KEY=YOUR_TENSORLAKE_API_KEY
export SNOWFLAKE_ACCOUNT=YOUR_SNOWFLAKE_ACCOUNT
export SNOWFLAKE_USER=YOUR_SNOWFLAKE_USER
export SNOWFLAKE_PASSWORD=YOUR_SNOWFLAKE_PASSWORD
export SNOWFLAKE_WAREHOUSE=YOUR_SNOWFLAKE_WAREHOUSE # `COMPUTE_WH'
export SNOWFLAKE_DATABASE=YOUR_SNOWFLAKE_DATABASE # 'AI_RISK_ANALYSIS'
export SNOWFLAKE_SCHEMA=YOUR_SNOWFLAKE_SCHEMA # 'SEC_FILINGS'
```

#### 3. Process a Test Filing

Run the processing script to extract data from a single test SEC filing:

```bash
python process-sec.py
```

#### 4. Query the Data

Query the extracted data (replace `5` with any query number 0-5):

```bash
python query-sec.py 5
```

### Deploying to Tensorlake Cloud

#### 1. Verify Tensorlake Connection

```bash
tensorlake whoami
```

#### 2. Set Secrets

```bash
tensorlake secrets set SNOWFLAKE_ACCOUNT='YOUR_SNOWFLAKE_ACCOUNT'
tensorlake secrets set SNOWFLAKE_USER='YOUR_SNOWFLAKE_USER'
tensorlake secrets set SNOWFLAKE_PASSWORD='YOUR_SNOWFLAKE_PASSWORD'
tensorlake secrets set SNOWFLAKE_WAREHOUSE='YOUR_SNOWFLAKE_WAREHOUSE'
tensorlake secrets set SNOWFLAKE_DATABASE='YOUR_SNOWFLAKE_DATABASE'
tensorlake secrets set SNOWFLAKE_SCHEMA='YOUR_SNOWFLAKE_SCHEMA'
```

#### 3. Verify Secrets

```bash
tensorlake secrets list
```

#### 4. Deploy Applications

Deploy the processing application:

```bash
tensorlake deploy process-sec.py
```

Deploy the query application:

```bash
tensorlake deploy query-sec.py
```

Once your applications have been deployed, you should be able to see them in your Applications on [cloud.tensorlake.ai](https://cloud.tensorlake.ai).

![A screenshot of the Tensorlake dashboard showing the two deployed applications `document_ingestion` and `query_sec`](./deployed-applications.png)

#### 5. Run the Full Pipeline

Process all SEC filings using the deployed application:

```bash
python process-sec-remote.py
```

To run a specific query using the deployed application:

*Note: specify a command line argument 0-5*
```bash
python sec-filings.py 2
```

## Files

- `process-sec.py` - Document processing application
- `query-sec.py` - Data query application  
- `process-sec-remote.py` - Script to run the deployed process-sec application
- `query-sec-remote.py` - Script to run the deployed query-sec application
- `README.md` - This file