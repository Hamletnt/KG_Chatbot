from typing import List, Optional
from langchain_neo4j import Neo4jGraph
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from langchain_community.vectorstores import Neo4jVector
from langchain_community.vectorstores.neo4j_vector import remove_lucene_chars
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from neo4j import GraphDatabase
import logging

from ..config import settings
from ..models.schemas import Entities

logger = logging.getLogger(__name__)

class GraphRAGService:
    def __init__(self):
        self.graph = None
        self.llm = None
        self.embeddings = None
        self.vector_index = None
        self.vector_retriever = None
        self.entity_chain = None
        self.chain = None
        self._initialize()
    
    def _initialize(self):
        """Initialize all components"""
        try:
            # Initialize Neo4j Graph
            self.graph = Neo4jGraph(
                url=settings.neo4j_uri,
                username=settings.neo4j_username,
                password=settings.neo4j_password
            )
            
            # Initialize Azure OpenAI LLM
            self.llm = AzureChatOpenAI(
                azure_endpoint=settings.azure_openai_endpoint,
                api_key=settings.azure_openai_api_key,
                azure_deployment=settings.azure_openai_chat_deployment,
                api_version=settings.azure_openai_api_version,
                temperature=0
            )
            
            # Initialize Azure OpenAI Embeddings
            self.embeddings = AzureOpenAIEmbeddings(
                azure_endpoint=settings.azure_openai_endpoint,
                api_key=settings.azure_openai_api_key,
                azure_deployment=settings.azure_openai_embeddings_deployment,
                api_version=settings.azure_openai_api_version
            )
            
            # Initialize Vector Index
            self.vector_index = Neo4jVector.from_existing_graph(
                self.embeddings,
                search_type="hybrid",
                node_label="Document",
                text_node_properties=["text"],
                embedding_node_property="embedding"
            )
            self.vector_retriever = self.vector_index.as_retriever()
            
            # Initialize Entity Chain
            self._setup_entity_chain()
            
            # Initialize Main Chain
            self._setup_main_chain()
            
            logger.info("GraphRAGService initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing GraphRAGService: {e}")
            raise
    
    def _setup_entity_chain(self):
        """Setup entity extraction chain"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are extracting organization and person entities from the text."),
            ("human", "Use the given format to extract information from the following input: {question}"),
        ])
        
        self.entity_chain = prompt | self.llm.with_structured_output(Entities)
    
    def _setup_main_chain(self):
        """Setup main RAG chain"""
        template = """Answer the question based only on the following context:
{context}

Question: {question}
Use natural language and be concise.
Answer:"""
        
        prompt = ChatPromptTemplate.from_template(template)
        
        self.chain = (
            {
                "context": self._full_retriever,
                "question": RunnablePassthrough(),
            }
            | prompt
            | self.llm
            | StrOutputParser()
        )
    
    def _graph_retriever(self, question: str) -> str:
        """Collects the neighborhood of entities mentioned in the question"""
        result = ""
        try:
            entities = self.entity_chain.invoke({"question": question})
            for entity in entities.names:
                response = self.graph.query(
                    """CALL db.index.fulltext.queryNodes('fulltext_entity_id', $query, {limit:2})
                    YIELD node,score
                    CALL {
                      WITH node
                      MATCH (node)-[r:!MENTIONS]->(neighbor)
                      RETURN node.id + ' - ' + type(r) + ' -> ' + neighbor.id AS output
                      UNION ALL
                      WITH node
                      MATCH (node)<-[r:!MENTIONS]-(neighbor)
                      RETURN neighbor.id + ' - ' + type(r) + ' -> ' +  node.id AS output
                    }
                    RETURN output LIMIT 50
                    """,
                    {"query": entity},
                )
                result += "\\n".join([el['output'] for el in response])
        except Exception as e:
            logger.error(f"Error in graph retrieval: {e}")
        
        return result
    
    def _full_retriever(self, question: str) -> str:
        """Combine graph and vector retrieval"""
        graph_data = self._graph_retriever(question)
        vector_data = [el.page_content for el in self.vector_retriever.invoke(question)]
        
        final_data = f"""Graph data:
{graph_data}
Vector data:
{"#Document ".join(vector_data)}
        """
        return final_data
    
    def chat(self, message: str) -> str:
        """Main chat method"""
        try:
            response = self.chain.invoke(message)
            return response
        except Exception as e:
            logger.error(f"Error in chat: {e}")
            return "I'm sorry, I encountered an error while processing your request."
    
    def chat_stream(self, message: str):
        """Streaming chat method"""
        try:
            # For now, simulate streaming by yielding the full response
            # In the future, this can be replaced with actual LLM streaming
            response = self.chain.invoke(message)
            
            # Simulate word-by-word streaming
            words = response.split()
            for word in words:
                yield word + " "
                
        except Exception as e:
            logger.error(f"Error in streaming chat: {e}")
            yield "I'm sorry, I encountered an error while processing your request."
    
    def health_check(self) -> dict:
        """Check the health of the service"""
        try:
            # Test Neo4j connection
            neo4j_status = False
            try:
                self.graph.query("RETURN 1")
                neo4j_status = True
            except:
                pass
            
            # Test Azure OpenAI connection
            azure_status = bool(
                settings.azure_openai_endpoint and 
                settings.azure_openai_api_key and 
                settings.azure_openai_chat_deployment
            )
            
            return {
                "status": "healthy" if neo4j_status and azure_status else "unhealthy",
                "neo4j_connected": neo4j_status,
                "azure_openai_configured": azure_status
            }
        except Exception as e:
            logger.error(f"Health check error: {e}")
            return {
                "status": "unhealthy",
                "neo4j_connected": False,
                "azure_openai_configured": False
            }
