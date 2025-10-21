import os
import json
from typing import List, Optional, Tuple, Any

from pydantic import BaseModel, Field
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas

from tensorlake.applications import Image, application, function, cls, RequestError, map
from tensorlake.documentai import (
    ChunkingStrategy, DocumentAI, ParsingOptions, PageClassConfig, 
    ParseResult, StructuredExtractionOptions
)

image = (
    Image(base_image="python:3.11-slim", name="snowflake-sec")
    .run("pip install snowflake-connector-python pandas pyarrow")
)

# Snowflake configuration - these should be set as secrets in production
SNOWFLAKE_CONFIG = {
    'account': os.getenv('SNOWFLAKE_ACCOUNT'),  # e.g., 'CBAYDTD-QMB46784'
    'user': os.getenv('SNOWFLAKE_USER'),
    'password': os.getenv('SNOWFLAKE_PASSWORD'),
    'warehouse': os.getenv('SNOWFLAKE_WAREHOUSE', 'COMPUTE_WH'),
    'database': 'AI_RISK_ANALYSIS',
    'schema': 'SEC_FILINGS'
}

class AIRiskMention(BaseModel):
    """Individual AI-related risk mention"""
    risk_category: str = Field(
        description="Category: Operational, Regulatory, Competitive, Ethical, Security, Liability"
    )
    risk_description: str = Field(description="Description of the AI risk")
    severity_indicator: Optional[str] = Field(None, description="Severity level if mentioned")
    citation: str = Field(description="Page reference")

class AIRiskExtraction(BaseModel):
    """Complete AI risk data from a filing"""
    company_name: str
    ticker: str
    filing_type: str
    filing_date: str
    fiscal_year: str
    fiscal_quarter: Optional[str] = None
    ai_risk_mentioned: bool
    ai_risk_mentions: List[AIRiskMention] = []
    num_ai_risk_mentions: int = 0
    ai_strategy_mentioned: bool = False
    ai_investment_mentioned: bool = False
    ai_competition_mentioned: bool = False
    regulatory_ai_risk: bool = False

@application()
@function(
    secrets=[
        "TENSORLAKE_API_KEY",
        "SNOWFLAKE_ACCOUNT",
        "SNOWFLAKE_USER", 
        "SNOWFLAKE_PASSWORD",
        "SNOWFLAKE_WAREHOUSE"
    ], 
    image=image
)
def document_ingestion(document_urls: List[str]) -> None:
    """Main entry point for document processing pipeline"""
    doc_ai = DocumentAI(api_key=os.getenv("TENSORLAKE_API_KEY"))
    
    # Initialize Snowflake tables
    initialize_snowflake_tables()
    
    page_classifications = [
        PageClassConfig(
            name="risk_factors",
            description="Pages that contain risk factors related to AI."
        ),
    ]
    parse_ids = {}

    for file_url in document_urls:
        try:
            parse_id = doc_ai.classify(
                file_url=file_url,
                page_classifications=page_classifications
            )
            parse_ids[file_url] = parse_id
            print(f"Successfully classified {file_url}: {parse_id}")

            #parse_ids[file_url] = "parse_jCcDRb6zq6T8j6W9LMTN7"
            #print(f"Successfully classified {file_url}")
        except Exception as e:
            print(f"Failed to classify document {file_url}: {e}")
    results = synchronize(map(extract_structured_data, parse_ids.items()))

    print(type(results))

    return results


@function(image=image)
def synchronize(futures: List[Any]) -> List[Any]:
    """Synchronize parallel processing results"""
    pass


@function(
    image=image, 
    secrets=[
        "TENSORLAKE_API_KEY",
        "SNOWFLAKE_ACCOUNT",
        "SNOWFLAKE_USER",
        "SNOWFLAKE_PASSWORD",
        "SNOWFLAKE_WAREHOUSE"
    ]
)
def extract_structured_data(url_parse_id_pair: Tuple[str, str]) -> None:
    """Extract structured data from classified pages"""
    print(f"Processing: {url_parse_id_pair}")
    
    doc_ai = DocumentAI(api_key=os.getenv("TENSORLAKE_API_KEY"))
    result = doc_ai.wait_for_completion(parse_id=url_parse_id_pair[1])
    #result = doc_ai.wait_for_completion(parse_id="parse_jCcDRb6zq6T8j6W9LMTN7")
    
    page_numbers = []
    for page_class in result.page_classes:
        if page_class.page_class == "risk_factors":
            page_numbers.extend(page_class.page_numbers)
    
    if not page_numbers:
        print(f"No risk factor pages found for {url_parse_id_pair[0]}")
        return None
    
    page_number_str_list = ",".join(str(i) for i in page_numbers)
    print(f"Extracting from pages: {page_number_str_list}")
    
    result = doc_ai.extract(
        file_url=url_parse_id_pair[0],
        page_range=page_number_str_list,
        structured_extraction_options=[
            StructuredExtractionOptions(
                schema_name="AIRiskExtraction", 
                json_schema=AIRiskExtraction
            )
        ]
    )
    
    #result = "parse_RCPnfHppLqm6dN6Qcbzdg"
    return write_to_snowflake(result, url_parse_id_pair[0])


@function(
    image=image, 
    secrets=[
        "TENSORLAKE_API_KEY",
        "SNOWFLAKE_ACCOUNT",
        "SNOWFLAKE_USER",
        "SNOWFLAKE_PASSWORD",
        "SNOWFLAKE_WAREHOUSE",
        "SNOWFLAKE_DATABASE",
        "SNOWFLAKE_SCHEMA"
    ]
)
def initialize_snowflake_tables() -> None:
    """Create Snowflake tables if they don't exist"""
    print("Connecting to Snowflake")
    conn = snowflake.connector.connect(
                account=os.getenv("SNOWFLAKE_ACCOUNT"),
                user=os.getenv("SNOWFLAKE_USER"),
                password=os.getenv("SNOWFLAKE_PASSWORD"),
                warehouse=os.getenv("SNOWFLAKE_WAREHOUSE")
    )
    cursor = conn.cursor()
    
    try:
        print("Creating database and schema")
        # Create database and schema
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {os.getenv('SNOWFLAKE_DATABASE')}")
        cursor.execute(f"USE DATABASE {os.getenv('SNOWFLAKE_DATABASE')}")
        cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {os.getenv('SNOWFLAKE_SCHEMA')}")
        cursor.execute(f"USE SCHEMA {os.getenv('SNOWFLAKE_SCHEMA')}")
        
        print("Creating AI Risk Filings table")
        # Create AI Risk Filings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS AI_RISK_FILINGS (
                COMPANY_NAME VARCHAR(100),
                TICKER VARCHAR(10),
                FILING_TYPE VARCHAR(10),
                FILING_DATE VARCHAR(20),
                FISCAL_YEAR VARCHAR(4),
                FISCAL_QUARTER VARCHAR(10),
                SOURCE_FILE VARCHAR(500),
                AI_RISK_MENTIONED BOOLEAN,
                AI_RISK_MENTIONS VARIANT,
                NUM_AI_RISK_MENTIONS INTEGER,
                AI_STRATEGY_MENTIONED BOOLEAN,
                AI_INVESTMENT_MENTIONED BOOLEAN,
                AI_COMPETITION_MENTIONED BOOLEAN,
                REGULATORY_AI_RISK BOOLEAN,
                AI_RISK_MENTIONS_JSON VARCHAR(16777216)
            )
        """)
        
        print("Creating Risk Mentions table")
        # Create Risk Mentions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS AI_RISK_MENTIONS (
                COMPANY_NAME VARCHAR(100),
                TICKER VARCHAR(10),
                FISCAL_YEAR VARCHAR(4),
                FISCAL_QUARTER VARCHAR(10),
                SOURCE_FILE VARCHAR(500),
                RISK_CATEGORY VARCHAR(50),
                RISK_DESCRIPTION VARCHAR(16777216),
                SEVERITY_INDICATOR VARCHAR(20),
                CITATION VARCHAR(100)
            )
        """)
        
        print("Snowflake tables initialized successfully")
        
    finally:
        cursor.close()
        conn.close()


@function(
    image=image, 
    secrets=[
        "TENSORLAKE_API_KEY",
        "SNOWFLAKE_ACCOUNT",
        "SNOWFLAKE_USER",
        "SNOWFLAKE_PASSWORD",
        "SNOWFLAKE_WAREHOUSE",
        "SNOWFLAKE_DATABASE",
        "SNOWFLAKE_SCHEMA"
    ]
)
def write_to_snowflake(parse_id: str, file_url: str) -> None:
    """Write extracted data to Snowflake"""
    import pandas as pd
    
    print("Writing data to Snowflake")
    doc_ai = DocumentAI(api_key=os.getenv("TENSORLAKE_API_KEY"))
    result: ParseResult = doc_ai.wait_for_completion(parse_id)
    
    if not result.structured_data:
        print(f"No structured data found for {file_url}")
        return
    
    # Prepare data
    raw = result.structured_data[0].data
    record = raw if isinstance(raw, dict) else (raw[0] if isinstance(raw, list) and raw else {})
    
    top_level = dict(record)
    mentions = top_level.pop("ai_risk_mentions", []) or []
    
    # Add source file reference
    source_file = os.path.basename(file_url)
    top_level['source_file'] = source_file
    
    # Serialize mentions for JSON column
    top_level['ai_risk_mentions_json'] = json.dumps(mentions)
    
    # Create DataFrames
    df_parent = pd.DataFrame([top_level])
    
    # Convert columns to uppercase for Snowflake
    df_parent.columns = [col.upper() for col in df_parent.columns]
    
    print("Connect to Snowflake")
    print("Snowflake credentials:")
    print("Account: ", os.getenv("SNOWFLAKE_ACCOUNT"))
    print("User: ", os.getenv("SNOWFLAKE_USER"))
    print("Password: ", os.getenv("SNOWFLAKE_PASSWORD"))
    print("Warehouse: ", os.getenv("SNOWFLAKE_WAREHOUSE"))
    # Connect to Snowflake
    conn = snowflake.connector.connect(
                account=os.getenv("SNOWFLAKE_ACCOUNT"),
                user=os.getenv("SNOWFLAKE_USER"),
                password=os.getenv("SNOWFLAKE_PASSWORD"),
                warehouse=os.getenv("SNOWFLAKE_WAREHOUSE")
    )
    cursor = conn.cursor()
    
    try:
        print("Specify database and schema")
        cursor.execute(f"USE DATABASE {os.getenv('SNOWFLAKE_DATABASE')}")
        cursor.execute(f"USE SCHEMA {os.getenv('SNOWFLAKE_SCHEMA')}")
        
        # Write parent table
        write_pandas(conn, df_parent, 'AI_RISK_FILINGS')
        print(f"Written filing data for {source_file}")
        
        # Process child table for mentions
        if isinstance(mentions, list) and mentions:
            df_mentions = pd.DataFrame(mentions)
            
            # Denormalize key columns for easy joins
            for col in ["company_name", "ticker", "fiscal_year", "fiscal_quarter"]:
                if col in top_level:
                    df_mentions[col] = top_level[col]
            
            df_mentions['source_file'] = source_file
            
            # Convert columns to uppercase
            df_mentions.columns = [col.upper() for col in df_mentions.columns]
            
            # Write mentions table
            write_pandas(conn, df_mentions, 'AI_RISK_MENTIONS')
            print(f"Written {len(df_mentions)} risk mentions for {source_file}")
        
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    from tensorlake.applications import run_local_application
    
    # Example usage with a single document
    test_urls = [
        "https://investors.confluent.io/static-files/95299e90-a988-42c5-b9b5-7da387691f6a"
    ]
    
    response = run_local_application(
        document_ingestion,
        test_urls
    )
    print(response.output())