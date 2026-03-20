import uuid
import sys
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException
from pathlib import Path
from utils.model_loader import ModelLoader
from datetime import datetime,timezone
import fitz
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores.faiss import FAISS

class SingleDocIngestor:
    def __init__(self,data_dir:str="data/single_document_chat",faiss_dir:str="faiss_index",session_id=None):
        try:
            self.log= CustomLogger().get_logger(__name__)
            self.data_dir=Path(data_dir)
            self.data_dir.mkdir(parents=True,exist_ok=True)
            self.faiss_dir=Path(faiss_dir)
            self.faiss_dir.mkdir(parents=True,exist_ok=True)
            self.model_loader=ModelLoader()
            self.log.info("SingleDocIngestor initialized",temp_path=str(self.data_dir),faiss_dir=str(self.faiss_dir))
        except Exception as e:
            self.log.error("Error initializing SingleDocIngestor", error=str(e))
            raise DocumentPortalException("Failed to initialize SingleDocIngestor", sys)  

    def ingest_files(self,uploaded_files):
        try:
            documents=[]
            for uploaded_file in uploaded_files:
                
                unique_filename = f"session_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.pdf"
                temp_path=self.data_dir/unique_filename
                with open(temp_path,"wb") as f_out:
                    f_out.write(uploaded_file.read())
                self.log.info("PDF saved for ingestion",filename=uploaded_file.name)
                loader=PyPDFLoader(str(temp_path))
                docs=loader.load()
                documents.extend(docs)
            self.log.info("PDF fles loaded",count=len(documents))
            return self._create_retriever(documents)     

        except Exception as e:
            self.log.error("Document Ingestion Failed", error=str(e))
            raise DocumentPortalException("Ingestion eror in SingleDocIngestor", sys)   


    def _create_retriever(self,documents):
        try:
            splitter=RecursiveCharacterTextSplitter(chunk_size=1000,chunk_overlap=300)
            chunks = splitter.split_documents(documents)
            self.log.info("Documents split into chunks",chunk_count=len(chunks))
            embeddings=self.model_loader.load_embeddings()
            vectorestore=FAISS.from_documents(documents=chunks,embedding=embeddings)
            # save FAISS index
            vectorestore.save_local(str(self.faiss_dir))
            self.log.info("FAISS index created and saved",faiss_path=str(self.faiss_dir))
            retriever=vectorestore.as_retriever(search_type="similarity",search_kwargs={"k":5})
            self.log.info("Retriever created successfully",retriever_type=str(type(retriever)))
            return retriever

        except Exception as e:
            self.log.error("Creating retriever failed", error=str(e))
            raise DocumentPortalException("Failed to create retriever in SingleDocIngestor", sys)

           