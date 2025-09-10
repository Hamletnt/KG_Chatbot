#!/usr/bin/env python3
"""
Script to initialize the graph database with data from dummytext.txt
"""
import os
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_openai import AzureChatOpenAI
from langchain_neo4j import Neo4jGraph
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

def main():
    """Initialize the graph database"""
    print("Initializing graph database...")
    
    # Check if all required environment variables are set
    required_vars = [
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_API_KEY", 
        "AZURE_OPENAI_CHAT_DEPLOYMENT",
        "NEO4J_URI",
        "NEO4J_USERNAME",
        "NEO4J_PASSWORD"
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print(f"Error: Missing environment variables: {missing_vars}")
        print("Please create a .env file based on .env.example")
        return 1
    
    try:
        # Initialize Neo4j Graph
        graph = Neo4jGraph(
            url=os.getenv("NEO4J_URI"),
            username=os.getenv("NEO4J_USERNAME"),
            password=os.getenv("NEO4J_PASSWORD")
        )
        print("✓ Connected to Neo4j")
        
        # Initialize LLM
        llm = AzureChatOpenAI(
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            azure_deployment=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01"),
            temperature=0
        )
        print("✓ Connected to Azure OpenAI")
        
        # Load and split documents
        if not os.path.exists("dummytext.txt"):
            print("Error: dummytext.txt not found")
            return 1
            
        loader = TextLoader(file_path="dummytext.txt")
        docs = loader.load()
        
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=250, chunk_overlap=24)
        documents = text_splitter.split_documents(documents=docs)
        print(f"✓ Loaded and split {len(documents)} document chunks")
        
        # Transform to graph documents
        llm_transformer = LLMGraphTransformer(llm=llm)
        graph_documents = llm_transformer.convert_to_graph_documents(documents)
        print(f"✓ Created {len(graph_documents)} graph documents")
        
        # Add to graph
        graph.add_graph_documents(
            graph_documents,
            baseEntityLabel=True,
            include_source=True
        )
        print("✓ Added documents to graph")
        
        # Create fulltext index
        try:
            driver = GraphDatabase.driver(
                uri=os.getenv("NEO4J_URI"),
                auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))
            )
            
            with driver.session() as session:
                session.run("""
                    CREATE FULLTEXT INDEX `fulltext_entity_id` 
                    FOR (n:__Entity__) 
                    ON EACH [n.id]
                """)
            print("✓ Created fulltext index")
            driver.close()
            
        except Exception as e:
            if "already exists" in str(e).lower():
                print("✓ Fulltext index already exists")
            else:
                print(f"Warning: Could not create fulltext index: {e}")
        
        print("\n🎉 Database initialization completed successfully!")
        print("You can now start the chatbot application.")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error during initialization: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
