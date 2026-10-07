"""Main entry point for the CopilotKit agent graph."""
from rfc3986.abnf_regexp import PATH_NOSCHEME

from pygenai.agent_builder import AgentBuilder
from pygenai.core.logger import get_logger
from pygenai.settings import get_settings
from pathlib import Path

from pygenai.rag.chunking import FixedSizeChunker
from pygenai.rag.loaders import TextLoader
from pygenai.rag.retrievers import HybridRetriever
from pygenai.rag.vectorstores import InMemoryVectorStore


logger = get_logger(__name__)
settings = get_settings()

agent_builder = AgentBuilder()

source = Path("./example_documents/rag_demo.txt")

loaded_documents = TextLoader().load(source)
chunker = FixedSizeChunker(chunk_size=220, overlap=40)

chunks = []
for document in loaded_documents:
    chunks.extend(chunker.chunk_document(document))

store = InMemoryVectorStore()
store.add_documents(chunks)

retriever = HybridRetriever(store)

agent_builder.add_rag_source("demo_source", retriever=retriever)


# Compile the workflow graph
graph = agent_builder.build()
