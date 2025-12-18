import os
from typing import List, Dict
from openai import OpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from .pinecone_setup import get_pinecone_index
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are Chill Panda 🐼 — a calm, empathetic mental health companion based on the book "The Chill Panda".
You respond warmly, supportively, and safely using wisdom from the book when relevant.
You do NOT give medical advice.
If user expresses distress, respond with empathy and encouragement.
Always maintain the persona of a wise, compassionate panda.
"""

class RAGChat:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            model=os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")
        )
        self.index = get_pinecone_index()
        self.vectorstore = PineconeVectorStore(index=self.index, embedding=self.embeddings, text_key="text")
        self.similarity_threshold = float(os.getenv("RAG_SIMILARITY_THRESHOLD", 0.7))
    
    def get_relevant_context(self, query: str, k: int = 3) -> str:
        """Retrieve relevant context from Pinecone"""
        try:
            docs = self.vectorstore.similarity_search_with_score(query, k=k)
            
            # Filter by similarity threshold
            relevant_docs = []
            for doc, score in docs:
                if score >= self.similarity_threshold:
                    relevant_docs.append(doc.page_content)
            
            if relevant_docs:
                context = "\n\n---\n\n".join(relevant_docs)
                return f"Relevant wisdom from The Chill Panda book:\n\n{context}"
            else:
                return ""
        except Exception as e:
            return ""
    
    def generate_response(self, user_message: str, conversation_history: List[Dict] = None) -> str:
        """Generate response using RAG when relevant, otherwise use general knowledge"""
        
        # Get relevant context from the book
        context = self.get_relevant_context(user_message)
        
        # Prepare messages for OpenAI
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
        
        # Add conversation history if available
        if conversation_history:
            for msg in conversation_history[-6:]:  # Last 6 messages for context
                messages.append({"role": msg["role"], "content": msg["content"]})
        
        # Add context if found
        if context:
            context_message = f"{context}\n\nBased on the above wisdom from The Chill Panda book, and as the Chill Panda, respond to: {user_message}"
            messages.append({"role": "user", "content": context_message})
        else:
            # If no relevant context, use general response
            messages.append({"role": "user", "content": user_message})
        
        try:
            response = client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                messages=messages,
                temperature=0.7,
                max_tokens=500,
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            # Fallback response
            return "I apologize, but I'm having trouble accessing my wisdom right now. Please try again, and remember to breathe deeply and stay calm. 🐼"

# Initialize RAG chat instance
rag_chat = RAGChat()

def generate_ai_reply(user_message: str, language: str, conversation_history: List[Dict] = None) -> str:
    """Generate AI reply using RAG system"""
    return rag_chat.generate_response(user_message, conversation_history)