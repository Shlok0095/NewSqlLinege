import os
import logging
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set API key explicitly as a fallback
os.environ["GROQ_API_KEY"] = "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"

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Debug: Print environment variables for troubleshooting
print("DEBUG: .env file loaded")
print(f"DEBUG: GROQ_API_KEY exists: {'GROQ_API_KEY' in os.environ}")
if 'GROQ_API_KEY' in os.environ:
    key_preview = os.environ.get("GROQ_API_KEY")[:10] + "..." if os.environ.get("GROQ_API_KEY") else "None"
    print(f"DEBUG: GROQ_API_KEY preview: {key_preview}")

try:
    from groq import Groq
    GROQ_AVAILABLE = True
    print("DEBUG: Groq package imported successfully")
except ImportError:
    logger.warning("Groq package not installed. LLM integration will not be available.")
    GROQ_AVAILABLE = False
    print("DEBUG: Groq package import failed")

class LLMIntegration:
    """Class for integrating with LLM models via Groq API for enhanced SQL lineage explanations."""
    
    def __init__(self):
        """Initialize the LLM integration."""
        # Try to get API key from environment, or use hardcoded key as fallback
        self.api_key = os.environ.get("GROQ_API_KEY")
        if not self.api_key:
            self.api_key = "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"
            
        print(f"DEBUG: In LLMIntegration.__init__, api_key exists: {self.api_key is not None}")
        
        self.is_available = GROQ_AVAILABLE and self.api_key is not None
        
        if not GROQ_AVAILABLE:
            logger.warning("Groq package not installed. Install with: pip install groq")
        
        if GROQ_AVAILABLE and not self.api_key:
            logger.warning("GROQ_API_KEY not found in environment variables. LLM integration will not be available.")
        
        if self.is_available:
            try:
                self.client = Groq(api_key=self.api_key)
                logger.info("Groq client initialized successfully")
            except Exception as e:
                logger.error(f"Error initializing Groq client: {str(e)}")
                self.is_available = False
                self.client = None
        else:
            self.client = None
    
    def is_enabled(self) -> bool:
        """Check if LLM integration is available and enabled."""
        return self.is_available
    
    def generate_sql_explanation(self, sql_statement: str) -> Optional[str]:
        """Generate an explanation for the given SQL statement."""
        if not self.is_enabled():
            return None
        
        prompt = f"""
        # SQL Query Analysis

        Below is a SQL query that needs detailed analysis. Your task is to explain exactly what this query does, focusing on data engineering aspects.

        ```sql
        {sql_statement}
        ```

        ## Analysis Requirements

        Please provide a comprehensive explanation that includes:

        1. **Main Purpose**: Explain the overall goal of this query in a concise one-sentence summary.
        
        2. **Data Sources**:
           - List all source tables and their purpose in the query
           - Identify temporary tables created during execution
           - Note any views or other data structures referenced
        
        3. **Data Flow & Transformations**:
           - Trace how data moves between tables step by step
           - Explain each major transformation (joins, aggregations, filtering)
           - Describe any complex calculations or business logic
           - Identify where and how data reshaping occurs
        
        4. **Output Structure**:
           - Describe the final output format and its columns
           - Explain the business meaning of calculated fields
           - Note any derived or transformed columns and their significance
        
        5. **Technical Considerations**:
           - Identify potential performance considerations
           - Note any SQL-specific techniques being used

        Format your response as a clear, technical explanation that would help a data engineer understand this query's purpose and flow. Use bullet points where appropriate for clarity.
        """
        
        try:
            completion = self.client.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=[
                    {"role": "system", "content": "You are an expert SQL analyzer specializing in data lineage and data engineering. You provide detailed, accurate, and technically precise explanations of SQL queries with a focus on data flow and transformations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,  # Lower temperature for more factual responses
                max_completion_tokens=1500,
                top_p=1,
                stream=False,
                stop=None,
            )
            
            explanation = completion.choices[0].message.content
            return explanation
            
        except Exception as e:
            logger.error(f"Error generating SQL explanation: {str(e)}")
            return None
    
    def generate_lineage_insights(self, column_mappings: Dict[str, List[str]], sql_statement: str) -> Optional[str]:
        """Generate insights about the data lineage."""
        if not self.is_enabled():
            return None
        
        # Convert column mappings to a readable format
        mappings_text = ""
        for target, sources in column_mappings.items():
            sources_str = ", ".join(sources)
            mappings_text += f"Target: {target} <- Sources: {sources_str}\n"
        
        prompt = f"""
        # Data Lineage Analysis and Optimization

        I need you to analyze both a SQL query and its resulting column-level lineage mappings to provide valuable data engineering insights.

        ## SQL Query
        ```sql
        {sql_statement}
        ```

        ## Column Lineage Mappings
        ```
        {mappings_text}
        ```

        ## Analysis Requirements

        Based on both the SQL and column mappings above, provide a comprehensive analysis including:

        1. **Data Flow Patterns**:
           - Visualize and explain the data flow from source to target tables
           - Identify central or key tables in the data pipeline
           - Explain how the column lineage demonstrates data transformations
           - Note any complex dependencies between tables and columns

        2. **Data Quality Considerations**:
           - Identify potential data quality issues or risks
           - Note any transformations that might impact data integrity
           - Highlight columns with complex transformations that may need validation
           - Identify potential null handling issues or type conversion concerns

        3. **Critical Path Analysis**:
           - Identify the most important tables and columns in this lineage
           - Determine which source tables/columns have the most downstream impact
           - Highlight any bottlenecks in the data flow

        4. **Optimization Recommendations**:
           - Suggest specific SQL optimization opportunities
           - Recommend any structural improvements to the query or data model
           - Identify opportunities for improved data pipeline design
           - Suggest monitoring points for data quality or performance

        Format your response as a detailed technical analysis with specific, actionable insights that would help a data engineer understand and improve this data pipeline.
        """
        
        try:
            completion = self.client.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=[
                    {"role": "system", "content": "You are a data lineage and SQL optimization expert with extensive experience in data engineering. You provide insightful, technical, and practical analysis of SQL data flows, with a focus on improvement opportunities and best practices."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_completion_tokens=1500,
                top_p=1,
                stream=False,
                stop=None,
            )
            
            insights = completion.choices[0].message.content
            return insights
            
        except Exception as e:
            logger.error(f"Error generating lineage insights: {str(e)}")
            return None
    
    def generate_response(self, prompt: str, system_prompt: str = None) -> Optional[str]:
        """
        Generate a response for a generic prompt.
        
        Args:
            prompt: The user prompt to send to the LLM
            system_prompt: Optional system prompt to set the context
            
        Returns:
            Optional[str]: The generated response or None if an error occurs
        """
        if not self.is_enabled():
            return None
        
        if system_prompt is None:
            system_prompt = "You are a helpful AI assistant specializing in data and SQL analysis."
        
        try:
            completion = self.client.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_completion_tokens=1500,
                top_p=1,
                stream=False,
                stop=None,
            )
            
            response = completion.choices[0].message.content
            return response
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return None
    
    def stream_response(self, prompt: str, system_prompt: str = None) -> Optional[str]:
        """Stream a response from the LLM and return the combined result."""
        if not self.is_enabled():
            return None
        
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            completion = self.client.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=messages,
                temperature=1,
                max_completion_tokens=1024,
                top_p=1,
                stream=True,
                stop=None,
            )
            
            # For streaming, we would normally yield chunks
            # But here we'll combine them for the full response
            full_response = ""
            for chunk in completion:
                content = chunk.choices[0].delta.content or ""
                full_response += content
                
            return full_response
            
        except Exception as e:
            logger.error(f"Error with streaming response: {str(e)}")
            return None
    
    def generate_text(self, prompt: str) -> Optional[str]:
        """
        Generate a short text description based on the given prompt.
        
        Args:
            prompt: The prompt asking for a description
            
        Returns:
            Optional[str]: The generated text or an empty string if an error occurs
        """
        if not self.is_enabled():
            return ""
        
        try:
            # Set up the generation parameters
            completion = self.client.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant specialized in describing database structures. Keep descriptions concise and informative, focusing on the likely purpose and content of database elements based on their names."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_completion_tokens=200,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
            
            # Extract and return the generated text
            return completion.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error generating text: {str(e)}")
            return "" 