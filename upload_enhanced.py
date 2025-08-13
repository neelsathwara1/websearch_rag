"""
Enhanced script to upload documents from various file formats to Qdrant
Supports: .txt, .md, .pdf, .docx files
"""

from qdrant_client import QdrantClient
from qdrant_client.http import models
import sentence_transformers
import json
import os
import re
from pathlib import Path
from config import QDRANT_URL, QDRANT_API_KEY

# File format processors
import PyPDF2
from docx import Document
import markdown

QDRANT_COLLECTION = "DM_docs"

# Connect to Qdrant Cloud
client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
print(f"Connected to Qdrant Cloud: {QDRANT_URL}")

# Initialize embedding model
model = sentence_transformers.SentenceTransformer("all-MiniLM-L6-v2")

def extract_text_from_pdf(file_path):
    """Extract text from PDF file"""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        print(f"Error reading PDF {file_path}: {e}")
        return ""

def extract_text_from_docx(file_path):
    """Extract text from DOCX file"""
    try:
        doc = Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text.strip()
    except Exception as e:
        print(f"Error reading DOCX {file_path}: {e}")
        return ""

def extract_text_from_markdown(file_path):
    """Extract text from Markdown file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            md_content = file.read()
        # Convert markdown to plain text (removes markdown formatting)
        html = markdown.markdown(md_content)
        # Remove HTML tags for plain text
        import re
        text = re.sub('<[^<]+?>', '', html)
        return text.strip()
    except Exception as e:
        print(f"Error reading Markdown {file_path}: {e}")
        return ""

def extract_text_from_txt(file_path):
    """Extract text from TXT file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read().strip()
    except Exception as e:
        print(f"Error reading TXT {file_path}: {e}")
        return ""

def chunk_text(text, max_chars=1000, overlap=100):
    """Split text into overlapping chunks for better retrieval"""
    if len(text) <= max_chars:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + max_chars
        
        # Try to end at a sentence boundary
        if end < len(text):
            # Look for sentence endings near the chunk boundary
            for i in range(end, max(start + max_chars - 200, start), -1):
                if text[i] in '.!?':
                    end = i + 1
                    break
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        start = end - overlap
        
        if start >= len(text):
            break
    
    return chunks

def process_documents_from_folder(folder_path="./documents"):
    """Process documents from a folder containing various file formats"""
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Created documents folder: {folder_path}")
        print("Please add your files (.txt, .md, .pdf, .docx) to this folder and run the script again")
        return []
    
    documents = []
    supported_extensions = {'.txt', '.md', '.pdf', '.docx'}
    
    for file_path in Path(folder_path).rglob('*'):
        if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
            print(f"Processing: {file_path.name}")
            
            # Extract text based on file type
            if file_path.suffix.lower() == '.pdf':
                text = extract_text_from_pdf(file_path)
            elif file_path.suffix.lower() == '.docx':
                text = extract_text_from_docx(file_path)
            elif file_path.suffix.lower() == '.md':
                text = extract_text_from_markdown(file_path)
            elif file_path.suffix.lower() == '.txt':
                text = extract_text_from_txt(file_path)
            else:
                continue
            
            if text:
                # Split large documents into chunks
                chunks = chunk_text(text, max_chars=800, overlap=100)
                
                for i, chunk in enumerate(chunks):
                    doc_id = f"{file_path.stem}_{i}" if len(chunks) > 1 else file_path.stem
                    documents.append({
                        'text': chunk,
                        'title': f"{file_path.stem} (Part {i+1})" if len(chunks) > 1 else file_path.stem,
                        'filename': file_path.name,
                        'source': str(file_path),
                        'file_type': file_path.suffix.lower(),
                        'chunk_id': i if len(chunks) > 1 else 0,
                        'total_chunks': len(chunks)
                    })
                
                print(f"  → Extracted {len(chunks)} chunk(s)")
            else:
                print(f"  → No text extracted from {file_path.name}")
    
    print(f"\nTotal documents processed: {len(documents)}")
    return documents

def upload_documents(documents):
    """Upload a list of documents to Qdrant"""
    if not documents:
        print("No documents to upload")
        return
    
    print(f"Uploading {len(documents)} document chunks...")
    
    points = []
    for i, doc in enumerate(documents):
        # Generate embedding
        embedding = model.encode(doc['text']).tolist()
        
        # Create point
        point = models.PointStruct(
            id=i,
            vector=embedding,
            payload={
                'text': doc['text'],
                'title': doc.get('title', f'Document {i}'),
                'filename': doc.get('filename', ''),
                'source': doc.get('source', 'unknown'),
                'file_type': doc.get('file_type', ''),
                'chunk_id': doc.get('chunk_id', 0),
                'total_chunks': doc.get('total_chunks', 1)
            }
        )
        points.append(point)
    
    # Upload to Qdrant in batches
    batch_size = 100
    for i in range(0, len(points), batch_size):
        batch = points[i:i + batch_size]
        try:
            client.upsert(
                collection_name=QDRANT_COLLECTION,
                points=batch
            )
            print(f"Uploaded batch {i//batch_size + 1}/{(len(points) + batch_size - 1)//batch_size}")
        except Exception as e:
            print(f"Error uploading batch {i//batch_size + 1}: {e}")
    
    try:
        # Show collection info
        info = client.get_collection(QDRANT_COLLECTION)
        print(f"Collection now has {info.points_count} points")
    except Exception as e:
        print(f"Error getting collection info: {e}")

def test_search(query="Facebook Ads targeting"):
    """Test search functionality"""
    print(f"\nTesting search with query: '{query}'")
    
    # Generate query embedding
    query_embedding = model.encode(query).tolist()
    
    # Search
    try:
        search_result = client.search(
            collection_name=QDRANT_COLLECTION,
            query_vector=query_embedding,
            limit=5
        )
        
        print("Search results:")
        for i, hit in enumerate(search_result):
            print(f"{i+1}. Score: {hit.score:.4f}")
            print(f"   Title: {hit.payload.get('title', 'No title')}")
            print(f"   File: {hit.payload.get('filename', 'Unknown')}")
            print(f"   Type: {hit.payload.get('file_type', 'Unknown')}")
            print(f"   Text: {hit.payload['text'][:150]}...")
            print()
    except Exception as e:
        print(f"Error during search: {e}")

if __name__ == "__main__":
    print("=== Enhanced Document Upload Tool ===")
    print("Supported formats: .txt, .md, .pdf, .docx")
    print()
    
    # Process documents from folder
    documents = process_documents_from_folder("./documents")
    
    if documents:
        # Upload documents
        upload_documents(documents)
        
        # Test search
        test_search("Facebook Ads targeting")
        test_search("business manager")
    else:
        print("No documents found to upload.")
        print("Add your files to the ./documents folder and run again.")
