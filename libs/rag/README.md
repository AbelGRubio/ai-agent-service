# Pygenai RAG (Retrieval-Augmented Generation)

![Python](https://img.shields.io/badge/Python-3.13%2B-3776AB?logo=python&logoColor=white)
![Package](https://img.shields.io/badge/package-pygenai--rag-8A2BE2)
![Status](https://img.shields.io/badge/status-experimental-orange)
![License](https://img.shields.io/badge/license-repository%20license-blue)

`pygenai-rag` is a comprehensive Python library for building Retrieval-Augmented Generation (RAG) systems. It provides modular, composable components for document loading, chunking, embedding, vector storage, and intelligent retrieval.

## 📚 Overview

RAG enhances large language models by retrieving relevant documents and providing them as context, enabling AI systems to answer questions based on custom data sources with better accuracy and relevance.

## 🎯 Core Components

### 1. **Loaders** - Document ingestion from multiple sources
Load documents from PDF, Markdown, CSV, Text, Web, and more. All documents are normalized to a standard `Document` class.

### 2. **Chunking** - Intelligent document splitting
Break large documents into semantically meaningful chunks using multiple strategies: fixed-size, token-based, semantic, and structural chunking.

### 3. **Embeddings** - Text-to-vector conversion
Transform documents into numerical representations that capture semantic meaning. Supports OpenAI embeddings and custom local models.

### 4. **VectorStores** - Efficient vector search and storage
Store embeddings and perform fast similarity searches. Supports multiple backends: In-Memory, FAISS, Chroma, Pinecone, and Qdrant.

### 5. **Retrievers** - Intelligent document retrieval
Implement search strategies including vector search, hybrid retrieval, and result reranking for optimal relevance.

## 📖 Detailed Documentation

For a comprehensive explanation of how each component works and their relationships, see **[RAG Components in Detail](./docs/rags_in_detail.md)**.

This detailed guide includes:
- **Component breakdown** with responsibilities and use cases
- **Available implementations** for each component type
- **The complete RAG pipeline** showing how components work together
- **Design principles** and architectural patterns
- **Performance considerations** and optimization tips
- **Common usage patterns** for different scenarios

## 🚀 Quick Start

### Installation

Install the package with uv:

```bash
uv add pygenai-rag
```

If you are working inside this monorepo, install the local package in editable mode:

```bash
uv pip install -e ./libs/rag
```

### Simple Example: Load → Chunk → Embed → Store → Retrieve

```python
from pygenai.rag.loaders import TextLoader
from pygenai.rag.chunking import FixedSizeChunker
from pygenai.rag.embeddings import OpenAIEmbeddings
from pygenai.rag.vectorstores import InMemoryVectorStore
from pygenai.rag.retrievers import VectorRetriever

# 1. Load documents
loader = TextLoader()
documents = loader.load("knowledge.txt")

# 2. Chunk documents
chunker = FixedSizeChunker(chunk_size=500, overlap=50)
chunks = chunker.chunk(documents)

# 3. Create embeddings
embedder = OpenAIEmbeddings(api_key="sk-...")

# 4. Store in vector database
vector_store = InMemoryVectorStore(embedder)
vector_store.add_documents(chunks)

# 5. Retrieve relevant documents
retriever = VectorRetriever(vector_store, top_k=5)
results = retriever.retrieve("What is machine learning?")

for doc in results:
    print(doc.content)
```

## 📁 Project Structure

```text
libs/rag/
├── docs/
│   └── rags_in_detail.md     # Comprehensive component guide
├── src/
│   └── pygenai/
│       └── rag/
│           ├── loaders/        # Document loading adapters
│           ├── chunking/        # Document splitting strategies
│           ├── embeddings/      # Text-to-vector conversion
│           ├── vectorstores/    # Vector search backends
│           ├── retrievers/      # Intelligent retrieval strategies
│           ├── files/           # File storage adapters
│           ├── data.py          # Core data models (Document)
│           └── __init__.py
├── tests/                       # Unit and integration tests
├── examples/                    # Example scripts and notebooks
├── README.md                    # This file
└── pyproject.toml              # Package configuration
```

## 🔧 Supported Backends

### Embeddings
- **OpenAI**: text-embedding-3-small, text-embedding-3-large
- **Local Models**: Custom embedding implementations

### VectorStores
- **In-Memory**: For development and testing
- **FAISS**: High-performance similarity search
- **Chroma**: Modern AI-native database
- **Pinecone**: Cloud-hosted vector database
- **Qdrant**: Open-source or managed vector database

### Chunking Strategies
- **Fixed-Size**: Simple, uniform chunk sizes
- **Token-Based**: Respects model token limits
- **Semantic**: Preserves meaning across boundaries
- **Structural**: Respects document structure (sections, headers)

### Document Loaders
- **PDFLoader**: Extract text from PDF files
- **TextLoader**: Load plain text files
- **MarkdownLoader**: Parse markdown with structure preservation
- **CSVLoader**: Load CSV data
- **WebLoader**: Fetch content from URLs
- **MultiFormatLoader**: Auto-detect and load multiple formats

### Retrieval Strategies
- **Vector Retrieval**: Pure similarity-based search
- **Hybrid Retrieval**: Combine vector + keyword search
- **Reranking**: Secondary ranking for improved relevance

## 📚 Learn More

### Component Architecture
For a deep dive into how each component works and their relationships, read **[RAG Components in Detail](./docs/rags_in_detail.md)**. This guide includes:
- Detailed explanation of each component's role
- Available implementations and their trade-offs
- Complete pipeline workflow
- Architectural design principles
- Performance optimization strategies
- Practical usage patterns for different scenarios

### Directory Structure
Each component lives in its own directory under `src/pygenai/rag/`:
- `loaders/` - Various document ingestion adapters
- `chunking/` - Different splitting strategies
- `embeddings/` - Embedding model integrations
- `vectorstores/` - Vector database backends
- `retrievers/` - Retrieval and ranking strategies
- `files/` - Storage system adapters
- `data.py` - Core data models

## 💡 Use Cases

**Knowledge Base Q&A**: Load company documentation, index it, and answer questions with context.

**Code Search**: Embed source code files, enable intelligent code search and navigation.

**Document Analysis**: Analyze large document collections and extract relevant information.

**Multi-Source RAG**: Combine documents from PDFs, websites, databases into a unified knowledge base.

**Semantic Search**: Go beyond keyword search with semantic understanding.

## Contributing

Contributions are welcome. To contribute:

1. Fork the repository and create a feature branch.
2. Add or update tests for behavior changes.
3. Keep the scope small and focused.
4. Run the relevant validation checks before submitting a pull request.
5. Open a PR with a clear summary of the change and why it matters.

Please keep code documentation clear and consistent with the repository style.

## License

This package is distributed under the repository's licensing terms for the Pygenai project. See the repository root for the full license text and any applicable notices.
