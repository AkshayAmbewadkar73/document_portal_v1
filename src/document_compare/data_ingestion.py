import sys
from pathlib import Path
from datetime import datetime,timezone
#from uuid import uuid4
import uuid
import fitz
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException

class DocumentIngestion:
    
    def  __init__(self,base_dir:str="data/document_compare",session_id=None):
        self.log=CustomLogger().get_logger(__name__)
        self.base_dir=Path(base_dir)
        self.session_id=session_id or f"session_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        self.session_path=self.base_dir/self.session_id
        self.session_path.mkdir(parents=True,exist_ok=True)
        self.log.info("DocumentComparator initialized",session_path=str(self.session_path))

    # def delete_existing_files(self,file_path):
    #     """
    #     Delete existing files at specified paths.
    #     """
    #     try:
    #         if self.base_dir.exists() and self.base_dir.is_dir():
    #             for file in self.base_dir.iterdir():
    #                 if file.is_file():
    #                     file.unlink()
    #                     self.log.info("File deleted",path=str(file))
    #             self.log.info("Directoru cleaned",ditectory=str(self.base_dir))        
    #     except Exception as e:
    #         self.log.error(f"Error deleting existing files:{e}")
    #         raise DocumentPortalException("An error occured while deleting existing files",sys)

    def save_uploaded_files(self,reference_file,actual_file):
        """
        Save the uploaded file to the specified directory.
        """
        try:
            # self.delete_existing_files(self.base_dir)
            # self.log.info('Existing files deleted successfully')
            ref_path=self.session_path/reference_file.name
            #ref_path=self.base_dir/actual_file.name
            act_path=self.session_path/actual_file.name
            #if not reference_file.endswith(".pdf") or not actual_file.endswith(".pdf"):
            if not reference_file.name.lower().endswith(".pdf") or not actual_file.name.lower().endswith(".pdf"):    
                raise ValueError("Only PDF files are supported")
            with open(ref_path,"wb") as f:
                f.write(reference_file.getbuffer())
            with open(act_path,"wb") as f:
                f.write(actual_file.getbuffer())
            self.log.info("Files saved",reference=str(ref_path),actual=str(act_path),session=self.session_id)
            return ref_path,act_path        
        except Exception as e:
            self.log.error(f"Error saving uploaded file:{e}")
            raise DocumentPortalException("An error occured while saving the uploaded file",sys)

    def read_pdf(self,pdf_path):
        """
        Read and extract text from a PDF file.
        """
        try:
            with fitz.open(pdf_path) as doc:
                if doc.is_encrypted:
                    raise ValueError('Pdf is encrypted:{pdf_path.name}')
                all_text=[]
                for page_num in range(doc.page_count):
                    page=doc.load_page(page_num)
                    text=page.get_text()
                    if text.strip():
                        all_text.append(f"\n---page{page_num+1}--\n{text}")
                self.log.info(f"PDF read successfully",file=str(pdf_path),pages=len(all_text))  
                return "\n".join(all_text)      
        except Exception as e:
            self.log.error(f"Error reading PDF:{e}")
            raise DocumentPortalException("An error occured while reading the PDF",sys)
        

    def combine_documents(self)->str:
        """
        Combine content of all PDFs in session folder into a single string.
        """
        
        try:
            
            doc_parts=[]

            for file in sorted(self.session_path.iterdir()):
                if file.is_file() and file.suffix.lower()==".pdf":
                    content=self.read_pdf(file)
                    doc_parts.append(f"Document: {file.name}\n{content}")

            combined_text="\n\n".join(doc_parts)
            self.log.info("Documents combined",count=len(doc_parts),session=self.session_id)
            return combined_text
        except Exception as e:
            self.log.error(f"Error combining documents",error=str(e),session=self.session_id)
            raise DocumentPortalException("An error occured while combining documents",sys) 

    def clean_old_session(self,keep_latest:int=3):
        """
        Optional method to delete older folders,keeping only the latest N
        """
        try:
            session_folders=sorted(
                [ f for f in self.base_dir.iterdir() if f.is_dir() ],
                reverse=True
            
            )   
            for folder in session_folders[keep_latest:]:
                for file in folder.iterdir():
                    
                        file.unlink()
                        
                folder.rmdir()
                self.log.info("old Session folder deleted",path=str(folder))
        except Exception as e:
            self.log.error(f"Error cleaning old sessions:{e}")
            raise DocumentPortalException("An error occured while cleaning old sessions",sys)        