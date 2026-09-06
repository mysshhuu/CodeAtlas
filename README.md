# CodeAtlas

> AI-powered codebase intelligence for understanding large software repositories.

CodeAtlas is a developer tool that lets you connect a GitHub repository, analyze its source code, search it using natural language, and understand its structure through an interactive dashboard.

Instead of manually searching through hundreds of files, developers can ask questions such as:

- Where is the `FastAPI` class implemented?
- How does routing work?
- How does FastAPI handle middleware?
- Where is authentication implemented?
- Which functions call this function?
- How is a particular feature structured?

CodeAtlas retrieves the most relevant parts of the repository and uses an LLM to generate an answer with source locations.

---

## Features

### 🔗 GitHub Repository Ingestion

CodeAtlas accepts a GitHub repository URL and automatically:

1. Clones the repository
2. Finds supported source files
3. Parses the source code
4. Extracts functions and classes
5. Creates code-aware chunks
6. Generates embeddings
7. Stores the embeddings in Qdrant

Currently supported source extensions include:

- Python
- JavaScript
- JSX
- TypeScript
- TSX

---

## 🧩 Code-Aware Chunking

Instead of splitting code into arbitrary pieces of text, CodeAtlas uses the Python AST parser to identify meaningful code structures such as:

- Functions
- Async functions
- Classes

Each chunk stores metadata including:

- File path
- Programming language
- Symbol name
- Symbol type
- Starting line
- Ending line

This allows the retrieval system to return meaningful pieces of source code instead of random text fragments.

---

## 🧠 Semantic Code Search

CodeAtlas converts code chunks into embedding vectors using OpenAI embeddings.

When a developer asks a question, the question is also converted into an embedding.

Qdrant then finds the code chunks that are semantically closest to the question.

The basic flow is:

```text
User Question
      ↓
Question Embedding
      ↓
Qdrant Vector Search
      ↓
Relevant Code Chunks
      ↓
LLM
      ↓
Answer + Sources