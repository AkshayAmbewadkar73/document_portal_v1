# #Test code for document ingestion and analysis using a PDFHandler and DocumentAnalyzer

# import os
# from pathlib import Path
# from src.document_analyzer.data_ingestion import DocumentHandler       # Your PDFHandler class
# from src.document_analyzer.data_analysis import DocumentAnalyzer  # Your DocumentAnalyzer class

# # Path to the PDF you want to test
# PDF_PATH = r"C:\\document_portal\\data\\document_analysis\\sample.pdf"

# # Dummy file wrapper to simulate uploaded file (Streamlit style)
# class DummyFile:
#     def __init__(self, file_path):
#         self.name = Path(file_path).name
#         self._file_path = file_path

#     def getbuffer(self):
#         return open(self._file_path, "rb").read()

# def main():
#     try:
#         # ---------- STEP 1: DATA INGESTION ----------
#         print("Starting PDF ingestion...")
#         dummy_pdf = DummyFile(PDF_PATH)

#         handler = DocumentHandler(session_id="test_ingestion_analysis")
        
#         saved_path = handler.save_pdf(dummy_pdf)
#         print(f"PDF saved at: {saved_path}")

#         text_content = handler.read_pdf(saved_path)
#         print(f"Extracted text length: {len(text_content)} chars\n")

#         # ---------- STEP 2: DATA ANALYSIS ----------
#         print("Starting metadata analysis...")
#         analyzer = DocumentAnalyzer()  # Loads LLM + parser
        
#         analysis_result = analyzer.analyze_document(text_content)

#         # ---------- STEP 3: DISPLAY RESULTS ----------
#         print("\n=== METADATA ANALYSIS RESULT ===")
#         for key, value in analysis_result.items():
#             print(f"{key}: {value}")

#     except Exception as e:
#         print(f"Test failed: {e}")

# if __name__ == "__main__":
#     main()

# Testing code for documnet comparistion usinfg the LLLm
# import io
# from pathlib import Path
# from src.document_compare.data_ingestion import DocumentIngestion
# from src.document_compare.document_comparator import DocumentComparatorLLM
# def load_fake_uploaded_file(file_path:Path):
#     return io.BytesIO(file_path.read_bytes())
# def test_compare_documnets():
#     ref_path=Path("C:\\document_portal_v1\\Data\\document_compare\\Long_Report_V1.pdf")
#     act_path=Path("C:\\document_portal_v1\\Data\\document_compare\\Long_Report_V2.pdf")

#     class FakeUpload:
#         def __init__(self,file_path:Path):
#             self.name=file_path.name
#             self._buffer=file_path.read_bytes()
#         def getbuffer(self):
#             return self._buffer    

#     comparator=DocumentIngestion()
#     ref_upload=FakeUpload(ref_path)
#     act_upload=FakeUpload(act_path)

#     ref_file,act_file=comparator.save_uploaded_files(ref_upload,act_upload)
#     combined_text=comparator.combine_documents()
#     comparator.clean_old_session(keep_latest=3)
#     print("\n Combined Text priew(First 1000 characters):\n")
#     print(combined_text[:1000])

#     llm_comparator=DocumentComparatorLLM()
#     comparison_df=llm_comparator.compare_documents(combined_text)
#     print("\n===COMPARISON RESULT DATAFRAME===\n")
#     print(comparison_df.head())
# if __name__=="__main__":
#     test_compare_documnets()


import sys
from pathlib import Path
from langchain_community.vectorstores.faiss import FAISS
from src.single_document_chat.data_ingestion import SingleDocIngestor
from src.single_document_chat.retrieval import ConversationalRAG
from utils.model_loader import ModelLoader
FAISS_INDEX_PATH=Path("faiss_index")

def test_conversational_rag_on_pdf(pdf_path:str,question:str):
    try:
        # Step 1: Ingest the PDF and create retriever
        model_loader=ModelLoader()
        if FAISS_INDEX_PATH.exists():
            print("Loading the existing FAISS index")
            embeddings=model_loader.load_embeddings()
            vectorestore=FAISS.load_local(folder_path=str(FAISS_INDEX_PATH),embeddings=embeddings,allow_dangerous_deserialization=True)
            retriever=vectorestore.as_retriever(search_type="similarity",search_kwargs={"k":5})
        else:
            print("Faiss index not found.Ingesting PDF and creating index")    
            with open(pdf_path,"rb") as f:
                uploaded_file=[f]
                ingestor=SingleDocIngestor()
                retriever=ingestor.ingest_files(uploaded_file)
        print("Running Conversational RAG")
        session_id="test_conversational_rag"
        rag=ConversationalRAG(session_id=session_id,retriever=retriever)
        response=rag.invoke(question)
        print(f"\n question:{question}\nAnswer:{response}")

    except Exception as e:
        print(f"Test failed: {e}")
        sys.exit(1)
if __name__=="__main__":
    pdf_path="C:\\document_portal_v1\\Data\\single_document_chat\\Attention_All_you_need.pdf"
    question="What are the main topics discussed in the document?"
 
    if not Path(pdf_path).exists():
        print(f"PDf file does not exist at:{pdf_path}")
        sys.exit(1)

    test_conversational_rag_on_pdf(pdf_path,question)
