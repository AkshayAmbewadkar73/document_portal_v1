# import os
# from utils.model_loader import ModelLoader
# from logger.custom_logger import CustomLogger
# from exception.custom_exception import DocumentPortalException
# from prompt.prompt_library import *
# from prompt.prompt_library import PROMPT_REGISTRY
# import sys
# from model.models import *
# #from model import Metadata
# from langchain_core.output_parsers.json import JsonOutputParser
# #from langchain.output_parsers.fix import OutputFixingParser
# from langchain_classic.output_parsers.fix import OutputFixingParser
# class DocumentAnalyzer:
#     'Analyzes documents using a pre-trained model.'
    
#     def __init__(self):
#         self.log = CustomLogger().get_logger(__name__)
#         try:
#             self.loader = ModelLoader()
#             self.llm = self.loader.load_llm()

#             # Prepare parsers
#             self.parser = JsonOutputParser(pydantic_object=Metadata)
#             self.fixing_parser = OutputFixingParser.from_llm(parser=self.parser, llm=self.llm)

#             # Load prompt
#             self.prompt = PROMPT_REGISTRY["document_analysis"]

#             self.log.info("DocumentAnalyzer initialized successfully")

#         except Exception as e:
#             self.log.error(f"Error initializing DocumentAnalyzer: {e}")
#             raise DocumentPortalException("Failed to initialize DocumentAnalyzer", e) from e
        

#     def analyze_document(self, document_text:str)-> dict:
#         """Analyze the document text and return structured metadata and summary"""
#         try:
#             chain=self.prompt|self.llm|self.parser
#             self.log.info("Meta data analysis chain initialized")

#             response = chain.invoke({
#                 "format_instructions": self.parser.get_format_instructions(),
#                 "document_text": document_text
#             })
#             self.log.info("Metadata extraction successful",key=list(response.keys()))

#             return response
#         except Exception as e:
#             self.log.error("Metadata analysis failed", error=str(e))
#             raise DocumentPortalException("Metadata extraction failed",sys)

import os
from utils.model_laoder import ModelLoader
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException
from model.models import *
from prompt.prompt_library import *
from prompt.prompt_library import PROMPT_REGISTRY

from langchain_core.output_parsers import JsonOutputParser
from langchain.output_parsers import OutputFixingParser

class DocumentAnalyzer:
    """Analyzes documents using a pre-trained model."""
    def __init__(self,):
        self.log=CustomLogger().get_logger(__name__)
        try:
            self.loader=ModelLoader()
            self.llm=self.loader.load_llm()
            self.parser=JsonOutputParser(pydantic_object=Metadata)
            self.fixing_parser=OutputFixingParser.from_llm(parser=self.parser,llm=self.llm)
            self.prompt=PROMPT_REGISTRY["document_analysis"]
            self.log.info("DocumentAnalyzer initialized successfully")
        except Exception as e:
            self.log.error(f"Error initializing DocumentAnalyzer: {e}")
            raise DocumentPortalException("Failed to initialize DocumentAnalyzer",e) from e
        
    def analyze_document(self,document_text:str)->dict:
        """Analyze the document text and return structured metadata and summary"""
        try:
            chain=self.prompt|self.llm|self.fixing_parser
            self.log.info("Meta data analysis chain initialized")
            response=chain.invoke({
                "format_intructions":self.parser.get_format_instructions(),
                "document_text":document_text  
            })
            self.log.info("Metadata extraction successful",key=list(response.keys()))
            return response
        except Exception as e:
            self.log.error("Metadata analysis failed", error=str(e))
            raise DocumentPortalException("Metadata extraction failed",e) from e

       
        
        