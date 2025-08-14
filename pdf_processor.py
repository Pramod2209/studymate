import PyPDF2
import io
import re
import logging
from typing import Optional, Union, BinaryIO

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFProcessor:
    def __init__(self):
        self.max_file_size = 10 * 1024 * 1024  # 10MB limit
        self.max_pages = 50  # Limit number of pages to process
    
    def _validate_pdf(self, file: BinaryIO) -> bool:
        """Validate PDF file"""
        try:
            # Check file size
            file.seek(0, 2)  # Move to end of file
            file_size = file.tell()
            file.seek(0)  # Reset file pointer
            
            if file_size > self.max_file_size:
                raise ValueError(f"File size {file_size/1024/1024:.2f}MB exceeds maximum allowed size of {self.max_file_size/1024/1024}MB")
                
            # Check if file is a valid PDF
            if file.read(4) != b'%PDF':
                raise ValueError("Invalid PDF file format")
                
            file.seek(0)  # Reset file pointer
            return True
            
        except Exception as e:
            logger.error(f"PDF validation failed: {str(e)}")
            raise
    
    def extract_text(self, uploaded_file: Union[BinaryIO, str]) -> str:
        """Extract text from uploaded PDF file with error handling"""
        try:
            if hasattr(uploaded_file, 'read'):  # Handle file-like object
                if not self._validate_pdf(uploaded_file):
                    raise ValueError("Invalid PDF file")
                
                # Read the uploaded file
                pdf_reader = PyPDF2.PdfReader(uploaded_file)
            else:  # Handle file path
                with open(uploaded_file, 'rb') as f:
                    if not self._validate_pdf(f):
                        raise ValueError("Invalid PDF file")
                    pdf_reader = PyPDF2.PdfReader(f)
            
            # Limit number of pages to process
            num_pages = min(len(pdf_reader.pages), self.max_pages)
            if num_pages < len(pdf_reader.pages):
                logger.warning(f"Processing only first {num_pages} pages of {len(pdf_reader.pages)}")
            
            text_parts = []
            for page_num in range(num_pages):
                try:
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    if text:
                        text_parts.append(text.strip())
                except Exception as e:
                    logger.error(f"Error processing page {page_num + 1}: {str(e)}")
                    continue
            
            return "\n\n".join(text_parts) if text_parts else ""
            
        except PyPDF2.errors.PdfReadError as e:
            logger.error(f"PDF read error: {str(e)}")
            raise ValueError("Failed to read PDF. The file might be corrupted or password protected.")
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            raise ValueError(f"Failed to process PDF: {str(e)}")
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        if not text:
            return ""
            
        try:
            # Remove excessive whitespace and normalize newlines
            text = ' '.join(text.split())
            
            # Fix common OCR/PDF extraction artifacts
            text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with single space
            text = re.sub(r'\s+([.,;:!?])', r'\1', text)  # Fix spaces before punctuation
            text = re.sub(r'([\w])-\s+([\w])', r'\1\2', text)  # Fix hyphenated words
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error cleaning text: {str(e)}")
            return text  # Return original text if cleaning fails
    
    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 100) -> list:
        """
        Split text into overlapping chunks for better retrieval
        """
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            if len(chunk.strip()) > 0:
                chunks.append(chunk)
        
        return chunks
    
    def extract_metadata(self, uploaded_file) -> dict:
        """
        Extract metadata from PDF
        """
        try:
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            metadata = {}
            
            if pdf_reader.metadata:
                metadata['title'] = pdf_reader.metadata.get('/Title', 'Unknown')
                metadata['author'] = pdf_reader.metadata.get('/Author', 'Unknown')
                metadata['subject'] = pdf_reader.metadata.get('/Subject', 'Unknown')
                metadata['creator'] = pdf_reader.metadata.get('/Creator', 'Unknown')
                metadata['producer'] = pdf_reader.metadata.get('/Producer', 'Unknown')
                metadata['creation_date'] = pdf_reader.metadata.get('/CreationDate', 'Unknown')
            
            metadata['num_pages'] = len(pdf_reader.pages)
            
            return metadata
            
        except Exception as e:
            return {'error': f"Could not extract metadata: {str(e)}"}
