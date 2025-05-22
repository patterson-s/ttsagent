import os
from typing import Dict, Any, Optional
from mistralai import Mistral


class OCRService:
    def __init__(self, api_key: str):
        self.client = Mistral(api_key=api_key)
    
    def upload_pdf(self, file_path: str) -> str:
        with open(file_path, "rb") as file:
            uploaded_file = self.client.files.upload(
                file={
                    "file_name": os.path.basename(file_path),
                    "content": file,
                },
                purpose="ocr"
            )
        return uploaded_file.id
    
    def get_signed_url(self, file_id: str) -> str:
        signed_url = self.client.files.get_signed_url(file_id=file_id)
        return signed_url.url
    
    def process_document(self, document_url: str) -> Optional[Dict[str, Any]]:
        try:
            ocr_response = self.client.ocr.process(
                model="mistral-ocr-latest",
                document={
                    "type": "document_url",
                    "document_url": document_url,
                }
            )
            return ocr_response.model_dump()
        except Exception as e:
            raise Exception(f"OCR processing failed: {str(e)}")
    
    def generate_markdown_content(self, ocr_data: Dict[str, Any]) -> str:
        markdown_text = ""
        for page in ocr_data.get("pages", []):
            page_number = page.get("index", "unknown")
            markdown_content = page.get("markdown", "")
            
            markdown_text += f"## Page {page_number}\n\n"
            markdown_text += markdown_content
            markdown_text += "\n\n---\n\n"
        
        return markdown_text