import sys
import os
from dotenv import load_dotenv
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_community.vectorstores import FAISS
#from langchain_core.runnable.history import RunnableWithMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_classic.chains import create_history_aware_retriever, create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain

from utils.model_loader import ModelLoader
from exception.custom_exception import DocumentPortalException
from logger.custom_logger import CustomLogger
from prompt.prompt_library import PROMPT_REGISTRY
from model.models import PromptType

class ConversationalRAG():
    def __init__(self,session_id:str,retriever):
        try:
            self.log=CustomLogger().get_logger(__name__)
            self.session_id=session_id
            self.retriever=retriever
            self.llm=self._load_llm()
            self.contextualize_prompt=PROMPT_REGISTRY[PromptType.CONTEXTUALIZE_QUESTION.value]
            self.qa_prompt=PROMPT_REGISTRY[PromptType.CONTEXT_QA.value]
            self.history_aware_retriever=create_history_aware_retriever(self.llm,self.retriever,self.contextualize_prompt)
            self.log.info("Created history-aware retriever",session_id=session_id)
            self.qa_chain=create_stuff_documents_chain(self.llm,self.qa_prompt)
            self.rag_chain=create_retrieval_chain(self.history_aware_retriever,self.qa_chain)
            self.log.info("Created rag chanin",session_id=session_id)
            self.chain=RunnableWithMessageHistory(
                self.rag_chain,
                self._get_session_history,
                input_messages_key="input",
                history_messages_key="chat_history",
                output_messages_key="answer"

            )

            self.log.info("created RunnablewithMessagesHistory",session_id=session_id)
        except Exception as e:
            self.log.error("Error initializing ConversationalRag",error=str(e))
            raise DocumentPortalException("Failed to initialize ConversationalRag",sys)



    def _load_llm(self):
        try:
            llm=ModelLoader().load_llm()
            self.log.info("LLM Loaded successfully", class_name=llm.__class__.__name__)
            return llm
        
        except Exception as e:
            self.log.error("Error loading LLM via ModelLoader", error=str(e))
            raise DocumentPortalException("Failed to load LLM in ConversationalRAG", sys) 
        
    def _get_session_history(self, session_id: str):
        try:
            # Create storage if not exists
            if not hasattr(self, "store"):
                self.store = {}

            # Create new session if not exists
            if session_id not in self.store:
                self.store[session_id] = ChatMessageHistory()

            return self.store[session_id]

        except Exception as e:
            self.log.error(
                "Error getting session history",
                error=str(e),
                session_id=session_id
            )
            raise DocumentPortalException(
                "Failed to get session history for ConversationalRag",
                sys
            )

    def load_retriever_from_faiss(self,index_path:str):
        try:
            embeddings=ModelLoader().load_embeddings()
            if not os.path.isdir(index_path):
                raise FileNotFoundError(f"FAISS index directory not found at {index_path}")
            vectorestore=FAISS.load_local(index_path,embeddings)
            self.log.info("Loaded FAISS index successfully",faiss_path=index_path)
            return vectorestore.as_retriever(search_type="similarity",search_kwargs={"k":5})
        
        except Exception as e:
            self.log.error("Error loading retriever from FAISS", error=str(e))
            raise DocumentPortalException("Failed to load retriever in ConversationalRAG", sys)
        
    def invoke(self,user_input:str):
        try:
            response=self.chain.invoke(
                {"input":user_input},
                config={"configurable":{"session_id":self.session_id}}
            )
            answer=response.get("answer","No answer")
            if not answer:
                self.log.warning("No answer generated from RAG chain",session_id=self.session_id)
            self.log.info("chain invoked successfully",session_id=self.session_id,user_input=user_input,answer_preview=answer[:150])  
            return answer
        except Exception as e:
            self.log.error("Failed to invoke conversational RAG", error=str(e),session_id=self.session_id)
            raise DocumentPortalException("Invocation error in ConversationalRAG", sys)    