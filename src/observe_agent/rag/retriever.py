"""Retriever module for indexing and querying documents using InMemoryVectorStore."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from langchain_community.document_loaders import TextLoader
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.retrievers import BaseRetriever
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from observe_core.logger import get_logger
from pydantic import PrivateAttr

from observe_agent.settings import get_settings

logger = get_logger(__name__)
settings = get_settings()


class Retriever(BaseRetriever):
    """Retriever class for indexing and querying documents using InMemoryVectorStore."""

    _embeddings: Embeddings = PrivateAttr()
    _hybrid: bool = PrivateAttr()
    _default_k: int = PrivateAttr()
    _vectorstore: InMemoryVectorStore = PrivateAttr()
    _documents: list[Document] = PrivateAttr(default_factory=list)

    @property
    def embeddings(self) -> Embeddings:
        """Return the embeddings instance."""
        return self._embeddings

    @property
    def hybrid(self) -> bool:
        """Return whether hybrid retrieval is enabled."""
        return self._hybrid

    @property
    def default_k(self) -> int:
        """Return the default number of documents to retrieve."""
        return self._default_k

    @property
    def vectorstore(self) -> InMemoryVectorStore:
        """Return the InMemoryVectorStore vectorstore."""
        return self._vectorstore

    @property
    def documents(self) -> list[Document]:
        """Return the list of documents for hybrid retrieval."""
        return self._documents

    def __init__(
        self,
        hybrid: bool = False,
        default_k: int = 4,
        **kwargs: Any,
    ) -> None:
        """Initialize the retriever with embeddings and InMemoryVectorStore vector store.

        Args:
            embeddings (Embeddings, optional): Embeddings object to use. If None, created based on model_choice.
            hybrid (bool, optional): Whether to use hybrid retrieval with BM25. Defaults to False.
            default_k (int, optional): Default number of documents to retrieve. Defaults to 4.
            **kwargs: Additional keyword arguments passed to BaseRetriever.
        """
        super().__init__(**kwargs)
        self._embeddings = self._define_embeddings()

        self._hybrid = hybrid
        self._default_k = default_k

        # Initialize empty InMemoryVectorStore index without texts
        self._vectorstore = InMemoryVectorStore.from_documents([], self._embeddings)
        self.load_documents_from_folder()

        if hybrid:
            self._documents = []

        logger.info(f"Retriever initialized with vector_db: faiss, hybrid: {hybrid}")

    def load_documents_from_folder(self) -> None:
        """Loads, splits, and adds all .md files in the specified folder to the vectorstore."""
        base_dir = Path(__file__).parent
        folder_path = base_dir / "docs"

        path = Path(folder_path)
        if not path.exists():
            logger.error(f"Folder {folder_path} does not exist.")
            return

        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)

        # Load all markdown files
        all_docs = []
        for file in path.glob("*.md"):
            loader = TextLoader(str(file), encoding="utf-8")
            all_docs.extend(loader.load())

        # Split and add
        split_docs = splitter.split_documents(all_docs)
        self._vectorstore.add_documents(split_docs)

        if self._hybrid:
            self._documents.extend(split_docs)

        logger.info(f"Successfully loaded {len(split_docs)} chunks from {folder_path}")

    def add_texts(self, texts: list[str], metadata: list[dict] | None = None) -> None:
        """Add a list of texts to the InMemoryVectorStore vector store and, if hybrid, to the documents list.

        Args:
            texts (list[str]): List of text documents to add.
            metadata (list[dict], optional): List of metadata dictionaries for each text.
        """
        if not texts:
            logger.warning("No texts provided to add_texts")
            return

        if metadata is None:
            metadata = [{}] * len(texts)
        if len(texts) != len(metadata):
            raise ValueError(f"Length of texts ({len(texts)}) must match metadatas ({len(metadata)})")

        documents = [Document(page_content=text, metadata=meta) for text, meta in zip(texts, metadata, strict=True)]
        self.vectorstore.add_documents(documents)
        if self.hybrid:
            self.documents.extend(documents)
        logger.info(f"Added {len(texts)} texts to the InMemoryVectorStore vector store")

    def retrieve(self, query: str, k: int = 4) -> list[Document]:
        """Retrieve the top k relevant documents for the given query.

        Args:
            query (str): The query string.
            k (int, optional): Number of documents to retrieve. Defaults to 4.

        Returns:
            list[Document]: List of relevant documents.
        """
        if not query.strip():
            logger.warning("Empty query provided")
            return []

        if self.hybrid:
            # NOTE: True BM25 hybrid retrieval is not yet implemented.
            # Falls back to vector-only search. Implement BM25 fusion here when needed.
            logger.warning("hybrid=True is set but BM25 is not yet implemented — using vector search only")

        return self.vectorstore.as_retriever(search_kwargs={"k": k}).invoke(query)

    def _get_relevant_documents(self, query: str, *, run_manager: object | None = None) -> list[Document]:
        """Implement abstract retrieval method required by BaseRetriever.

        Args:
            query (str): The query string.
            run_manager (object, optional): Run manager for tracking. Defaults to None.

        Returns:
            list[Document]: List of relevant documents.
        """
        return self.retrieve(query, k=self.default_k)

    @staticmethod
    def _define_embeddings() -> OpenAIEmbeddings:
        """Create and return the OpenAI embeddings client.

        This helper centralizes embedding client construction so that the
        Retriever can instantiate embeddings consistently. The returned client
        is configured with the application OpenAI API key and a fixed model.

        Returns:
            OpenAIEmbeddings: Configured embeddings instance.
        """
        return OpenAIEmbeddings(
            api_key=settings.openai_api_key,
            model="text-embedding-3-small",
        )


if __name__ == "__main__":
    # Example usage for testing
    sample_texts = [
        "Python is a versatile programming language.",
        "Java is used for enterprise applications.",
    ]

    # Test with InMemoryVectorStore
    retriever_faiss = Retriever()
    retriever_faiss.add_texts(sample_texts)
    query = "enterprise"
    results = retriever_faiss.retrieve(query)
    for i, doc in enumerate(results):
        logger.info(f"InMemoryVectorStore Result {i + 1}: {doc.page_content[:100]}...")

    # Test with hybrid retrieval (using InMemoryVectorStore)
    retriever_hybrid = Retriever(hybrid=True)
    retriever_hybrid.add_texts(sample_texts)
    results = retriever_hybrid.retrieve(query)
    for i, doc in enumerate(results):
        logger.info(f"Hybrid Result {i + 1}: {doc.page_content[:100]}...")
