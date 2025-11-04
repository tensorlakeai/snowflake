from tensorlake.applications import Image, application, function
import os
import snowflake.connector

image = (
    Image(base_image="python:3.11-slim", name="snowflake-sec")
    .run("pip install snowflake-connector-python wikipedia openai")
)

@application()
@function(
    image=image,
    secrets=["OPENAI_API_KEY"]
)
def query_wikipedia(query: str) -> None:
    import openai
    
    try:
        # Set OpenAI API key
        openai.api_key = os.getenv("OPENAI_API_KEY")
        
        # Use OpenAI to extract the best Wikipedia topic from the query
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that extracts the main topic from a user query that would be best answered by a Wikipedia article. Return only the topic name, nothing else. The topic should be suitable for a Wikipedia URL."
                },
                {
                    "role": "user",
                    "content": f"What Wikipedia article would best answer this query: {query}"
                }
            ],
            temperature=0
        )
        
        topic = response.choices[0].message.content.strip()
        print(f"Query: {query}")
        print(f"Best Wikipedia topic: {topic}")
        
        # Construct Wikipedia URL
        url = f"https://en.wikipedia.org/wiki/{topic.replace(' ', '_')}"
        print(f"Wikipedia URL: {url}")

        return extract_wikipedia_page(query, url)

    except Exception as e:
        print(f"Error in query_wikipedia: {e}")
        raise

@function(
    image=image
)
def extract_wikipedia_page(query: str, url: str) -> None:
    import wikipedia
    
    try:
        # Extract page title from URL
        title = url.split('/wiki/')[-1].replace('_', ' ')
        
        # Get page content
        page = wikipedia.page(title, auto_suggest=False)

        return chunk_text_with_tensorlake(query, page.title, page.content)

    except Exception as e:
        print(f"Error in extract_wikipedia_page: {e}")
        raise

@function(
    image=image,
    secrets = [
        "TENSORLAKE_API_KEY"
    ]
)
def chunk_text_with_tensorlake(query: str, title: str, content: str) -> list:
    from tensorlake.documentai import DocumentAI, ParsingOptions, ChunkingStrategy, MimeType

    print(f"Chunking text for page: {title}")
    print(content)

    """Chunk text using Tensorlake's text chunking service"""
    try:
        doc_ai = DocumentAI(api_key=os.getenv("TENSORLAKE_API_KEY"))
        
        print("Parsing and chunking text with Tensorlake DocumentAI")
        result = doc_ai.parse_and_wait(
            file=content,
            mime_type=MimeType.TEXT,
            parsing_options=ParsingOptions(
                chunking_strategy=ChunkingStrategy.SECTION
            )
        )

        print(f"Text chunked into {len(result.chunks)} chunks using Tensorlake")
        return write_to_snowflake(query, title, result.chunks)

    except Exception as e:
        print(f"Error in chunk_text_with_tensorlake: {e}")
        raise

@function(
    image=image,
    secrets = [
        "SNOWFLAKE_ACCOUNT",
        "SNOWFLAKE_USER",
        "SNOWFLAKE_PASSWORD",
        "SNOWFLAKE_WAREHOUSE",
        "SNOWFLAKE_DATABASE",
        "SNOWFLAKE_SCHEMA"
    ]
)
def write_to_snowflake(query: str, title: str, chunks: list) -> None:
    import os
    import snowflake.connector
    import snowflake

    """Write Wikipedia page content to Snowflake and create chunks using Cortex"""
    try:
        print("Connecting to Snowflake to write data")
        conn = snowflake.connector.connect(
                    account=os.getenv("SNOWFLAKE_ACCOUNT"),
                    user=os.getenv("SNOWFLAKE_USER"),
                    password=os.getenv("SNOWFLAKE_PASSWORD"),
                    warehouse=os.getenv("SNOWFLAKE_WAREHOUSE")
        )
        cursor = conn.cursor()

        print("Creating database and schema")
        # Create database and schema
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {os.getenv('SNOWFLAKE_DATABASE')}")
        cursor.execute(f"USE DATABASE {os.getenv('SNOWFLAKE_DATABASE')}")
        cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {os.getenv('SNOWFLAKE_SCHEMA')}")
        cursor.execute(f"USE SCHEMA {os.getenv('SNOWFLAKE_SCHEMA')}")
      
        print("Creating Wikipedia Chunks table for Cortex Search")
        # Create Wikipedia Chunks table - simplified for Cortex Search
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS WIKIPEDIA_CHUNKS (
                CHUNK_ID VARCHAR(255),
                TITLE VARCHAR(255),
                CHUNK_TEXT TEXT,
                CHUNK_INDEX NUMBER,
                CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
                PRIMARY KEY (CHUNK_ID)
            )
        """)
        
        print("Snowflake tables initialized successfully")
        
        # Insert each chunk into the WIKIPEDIA_CHUNKS table
        for index, chunk in enumerate(chunks):
            chunk_id = f"{title}_chunk_{index}"  # Create a unique chunk ID
            cursor.execute("""
                INSERT INTO WIKIPEDIA_CHUNKS (CHUNK_ID, TITLE, CHUNK_TEXT, CHUNK_INDEX)
                VALUES (%s, %s, %s, %s)
            """, (
                chunk_id,
                title,
                chunk.content,  # Use chunk.content for the chunk text
                index
            ))
        
        chunks_count = cursor.fetchone()
        print(f"Created chunks for: {title}")
        
        # Enable change tracking for Cortex Search (if not already enabled)
        cursor.execute("""
            ALTER TABLE WIKIPEDIA_CHUNKS SET CHANGE_TRACKING = TRUE
        """)
        
        # Create or replace Cortex Search Service
        print("Creating/Updating Cortex Search Service")
        cursor.execute("""
            CREATE OR REPLACE CORTEX SEARCH SERVICE WIKIPEDIA_SEARCH_SERVICE
            ON CHUNK_TEXT
            ATTRIBUTES TITLE, METADATA
            WAREHOUSE = %s
            TARGET_LAG = '1 minute'
            AS (
                SELECT 
                    CHUNK_ID,
                    CHUNK_TEXT,
                    TITLE,
                    METADATA
                FROM WIKIPEDIA_CHUNKS
            )
        """, (os.getenv("SNOWFLAKE_WAREHOUSE"),))
        
        print(f"Cortex Search Service created/updated successfully")
        
        # Commit the transaction
        conn.commit()
        
    except Exception as e:
        print(f"Error writing to Snowflake: {e}")
        raise
        
    finally:
        cursor.close()
        conn.close()

    return query_snowflake_wikipedia(query)

@function(
    image=image,
    secrets=[
        "SNOWFLAKE_ACCOUNT",
        "SNOWFLAKE_USER",
        "SNOWFLAKE_PASSWORD",
        "SNOWFLAKE_WAREHOUSE",
        "SNOWFLAKE_DATABASE",
        "SNOWFLAKE_SCHEMA"
    ]
)
def query_snowflake_wikipedia(query: str) -> None:
    import os
    import snowflake.connector

    """Query Snowflake Wikipedia chunks using Cortex Search"""
    context = ""  # Initialize context with empty string
    try:
        print("Connecting to Snowflake to query data")
        conn = snowflake.connector.connect(
                    account=os.getenv("SNOWFLAKE_ACCOUNT"),
                    user=os.getenv("SNOWFLAKE_USER"),
                    password=os.getenv("SNOWFLAKE_PASSWORD"),
                    warehouse=os.getenv("SNOWFLAKE_WAREHOUSE")
        )
        cursor = conn.cursor()
        
        cursor.execute(f"USE DATABASE {os.getenv('SNOWFLAKE_DATABASE')}")
        cursor.execute(f"USE SCHEMA {os.getenv('SNOWFLAKE_SCHEMA')}")
        
        print(f"Querying Wikipedia chunks using Cortex Search for: {query}")
        
        # Method 1: Try using Cortex Search Service (recommended)
        try:
            cursor.execute("""
                SELECT 
                    CHUNK_TEXT,
                    TITLE,
                    SEARCH_SCORE() as score
                FROM TABLE(
                    WIKIPEDIA_SEARCH_SERVICE.SEARCH(
                        query => %s,
                        columns => ['CHUNK_TEXT'],
                        limit => 5
                    )
                )
                ORDER BY score DESC
            """, (query,))
            
            results = cursor.fetchall()
            
            if results:
                print(f"Found {len(results)} relevant chunks using Cortex Search")
                for row in results:
                    print(f"Score: {row[2]:.3f}, Title: {row[1]}, Chunk: {row[0][:100]}...")
                
                # Combine chunks into context
                context = "\n\n---\n\n".join([
                    f"[From: {row[1]}]\n{row[0]}" 
                    for row in results
                ])
            else:
                print("No relevant chunks found with Cortex Search")
                
        except Exception as search_error:
            print(f"Cortex Search Service not available: {search_error}")
            print("Trying alternative Cortex search methods...")
            
            # Method 2: Try using Cortex SEARCH function directly
            try:
                cursor.execute("""
                    SELECT 
                        CHUNK_TEXT,
                        TITLE,
                        SNOWFLAKE.CORTEX.SEARCH(
                            %s, 
                            CHUNK_TEXT
                        ) as similarity
                    FROM WIKIPEDIA_CHUNKS
                    WHERE similarity > 0.5
                    ORDER BY similarity DESC
                    LIMIT 5
                """, (query,))
                
                results = cursor.fetchall()
                
                if results:
                    print(f"Found {len(results)} relevant chunks using Cortex SEARCH")
                    context = "\n\n---\n\n".join([
                        f"[From: {row[1]}]\n{row[0]}" 
                        for row in results
                    ])
                    
            except Exception as e2:
                print(f"Cortex SEARCH function also not available: {e2}")
                
                # Method 3: Fallback to simple text search
                print("Using fallback text search...")
                cursor.execute("""
                    SELECT 
                        CHUNK_TEXT,
                        TITLE
                    FROM WIKIPEDIA_CHUNKS
                    WHERE CONTAINS(LOWER(CHUNK_TEXT), LOWER(%s))
                    LIMIT 5
                """, (query,))
                
                results = cursor.fetchall()
                
                if results:
                    context = "\n\n---\n\n".join([
                        f"[From: {row[1]}]\n{row[0]}" 
                        for row in results
                    ])
                else:
                    # Last resort - get any chunks
                    cursor.execute("""
                        SELECT CHUNK_TEXT, TITLE 
                        FROM WIKIPEDIA_CHUNKS 
                        LIMIT 5
                    """)
                    results = cursor.fetchall()
                    if results:
                        context = "\n\n---\n\n".join([
                            f"[From: {row[1]}]\n{row[0]}" 
                            for row in results
                        ])
                    else:
                        context = "No Wikipedia content available in the database."
            
    except Exception as e:
        print(f"Error querying Snowflake: {e}")
        context = f"Unable to retrieve Wikipedia content due to an error: {str(e)}"
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

    return answer_query_with_wikipedia(query, context)

@function(
    image=image,
    secrets=["OPENAI_API_KEY"]
)
def answer_query_with_wikipedia(query: str, context: str) -> str:
    """Answer user query using Wikipedia chunks"""
    import openai
    
    try:
        # Set OpenAI API key
        openai.api_key = os.getenv("OPENAI_API_KEY")
        
        # Use OpenAI to answer the query based on the context
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are a knowledgeable assistant that answers user queries based on provided Wikipedia content. If the context doesn't contain relevant information, say so."
                },
                {
                    "role": "user",
                    "content": f"Using the following Wikipedia content, answer the query: {query}\n\nContext:\n{context}"
                }
            ],
            temperature=0
        )
        
        answer = response.choices[0].message.content.strip()
        print(f"\n=== ANSWER ===\n{answer}\n")
        
        return answer

    except Exception as e:
        print(f"Error answering query with Wikipedia: {e}")
        return f"Error generating answer: {str(e)}"

if __name__ == "__main__":
    from tensorlake.applications import run_local_application
    
    # Example usage
    query = "How do snowflakes form in the atmosphere?"
    
    response = run_local_application(
        query_wikipedia,
        query
    )
    print("\nFinal output:", response.output())