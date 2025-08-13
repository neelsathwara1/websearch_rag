# Web RAG with OpenAI

A Retrieval-Augmented Generation (RAG) system powered by OpenAI's GPT and embeddings, combined with SerpAPI for web search and Qdrant for vector storage.

## Features

- **OpenAI Integration**: Uses GPT-3.5-turbo for text generation and text-embedding-ada-002 for embeddings
- **Document Upload**: Supports PDF, DOCX, Markdown, and TXT files
- **Vector Search**: Qdrant cloud database for semantic document retrieval
- **Web Search**: SerpAPI integration for real-time web information
- **FastAPI Server**: RESTful API for easy integration

## Setup

### 1. Install Dependencies

```bash
pip install -r req.txt
```

### 2. Configure Environment Variables

Create a `.env` file with:

```
OPENAI_API_KEY=your_openai_api_key_here
SERPAPI_API_KEY=your_serpapi_key_here
QDRANT_URL=your_qdrant_cloud_url
QDRANT_API_KEY=your_qdrant_api_key
```

### 3. Upload Documents

Use the OpenAI-optimized upload script:

```bash
python upload_openai.py
```

This will:
- Create a new collection `DM_docs_openai` optimized for OpenAI embeddings (1536 dimensions)
- Process documents from the `./documents` folder
- Generate embeddings using OpenAI's text-embedding-ada-002
- Upload to your Qdrant cloud database

### 4. Test the System

Test OpenAI API connectivity:

```bash
python test_openai.py
```

Test the complete RAG system:

```bash
python test_direct.py
```

### 5. Start the Server

```bash
python -m uvicorn app:app --host 0.0.0.0 --port 8001
```

## API Usage

### Health Check
```bash
GET /
```

### Ask a Question
```bash
POST /ask
Content-Type: application/json

{
    "query": "What are Facebook ad targeting options?"
}
```

### Debug Information
```bash
GET /debug
```

## Key Differences from Gemini Version

1. **Embeddings**: Uses OpenAI's text-embedding-ada-002 (1536 dimensions) instead of sentence-transformers
2. **Text Generation**: Uses GPT-3.5-turbo instead of Gemini
3. **Collection**: Uses `DM_docs_openai` collection optimized for OpenAI embeddings
4. **Rate Limits**: Smaller batch sizes to respect OpenAI rate limits
5. **Error Handling**: Simplified error handling for OpenAI's more stable API

## File Structure

- `app.py` - FastAPI application
- `orchestrator.py` - Main query processing logic with OpenAI
- `rag_module.py` - Document retrieval with OpenAI embeddings
- `search_module.py` - SerpAPI web search
- `upload_openai.py` - Document upload with OpenAI embeddings
- `test_openai.py` - OpenAI API tests
- `test_direct.py` - End-to-end system tests
- `config.py` - Configuration management

## Supported Document Types

- **PDF**: Extract text from PDF files
- **DOCX**: Microsoft Word documents
- **Markdown**: .md files with formatting preserved
- **TXT**: Plain text files

## Logging

All operations are logged to:
- Console output
- `app.log` file

Set logging level in the code or use `logging.basicConfig(level=logging.DEBUG)` for verbose output.

## Cost Considerations

- **OpenAI Embeddings**: ~$0.0001 per 1K tokens
- **OpenAI GPT-3.5-turbo**: ~$0.002 per 1K tokens
- **SerpAPI**: 100 free searches/month, then paid
- **Qdrant Cloud**: Free tier available

Monitor your usage in the OpenAI dashboard and SerpAPI account.
