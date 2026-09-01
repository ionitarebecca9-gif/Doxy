# Doxy - AI Document Assistant (RAG System)

Doxy is a local Retrieval-Augmented Generation application that allows users to upload documents (PDF, DOCX, TXT) and chat with an AI assistant that answers questions strictly based on the provided documents.

## Key features

* **Multi-format support:** Read and process `.pdf`, `.docx` and `.txt` files.
* **OCR and image preprocessing:** Automatically detects scanned PDFs and extracts text using Tesseract. It applies grayscale conversion and contrast enhancement to bypass watermarks.
* **Context-aware memory:** The AI remembers the context of the conversation so that the user can ask follow-up questions.

## Arhitecture and technologies

### Backend (Python)

* **Flask:** Framework to handle HTTP requests between the frontend and the AI logic.
* **LangChain:** Used for document loading and text splitting.
* **ChromaDB:** Local vector database to store document embeddings.
* **Groq API:** The core LLM used for generating responses is an OpenAI model, provided by Groq.
* **PyMuPDF and Tesseract:** Used for scanned PDFs.

### Frontend (HTML, CSS, JS)

* **HTML and CSS:** Used for theme switching, flexbox layouts and responsive design.
* **Vanilla JavaScript:** Used for a better user experience and high interactability.

## How it works

When a user uploads a document, the file is saved locally.If it's a PDF, it attempts to extract raw text. If the extracted text is less than 50 characters, the system flags it as a "Scanned Document" and triggers the OCR module. The extracted text is split into smaller chunks (1000 characters per chunk with a 200-character overlap to preserve context between paragraphs). `ChromaDB` uses the HuggingFace model to convert these chunks into vector embeddings and saves them in the `./chroma_database` folder.

When the user asks a question, `ai_agent.py` intercepts the question. If it's a follow-up question the script prepends the AI's last answer to the current query.
The top 8 most semantically similar chunks are retrieved from the database, along with their metadata (Filename and Page Number). The AI reads the context, generates the answer, and sends it back to the frontend, which displays the text and the corresponding source chips.

## System evaluation

### Types of questions the application handles well
The system excels in scenarios where the user seeks specific information contained within the text:
* **Direct fact retrieval:** Questions like *"What is the company's CUI?"* are answered with near 100% accuracy.
* **Summarization:** Requests like *"Summarize the responsibilities of the employee"* work well because the vector database retrieves the most dense chunks containing those keywords.
* **Contextual follow-ups:** Thanks to the conversational memory implementation (injecting the AI's previous answer into the new search query), the system successfully handles pronoun resolutions

### Situations with incomplete or incorrect answers
There are specific edge cases where the RAG pipeline struggles:
* **Complex data tables:** If a PDF contains complex tables (e.g., financial balance sheets), the text extractor or OCR reads them left-to-right, top-to-bottom, losing the row/column structural meaning. The AI might fail to answer *"What was the revenue for 2023?"* if the year and the value were split across different chunks.
* **Multi-document synthesis:** If a user asks *"What are all the differences between Document A and Document B?"*, the system might fail. The vector search retrieves only the top 8 chunks (k=8) that semantically match the prompt, meaning it might miss broader context spread across multiple pages.
* **Heavy OCR noise:** Documents with stamps over text, handwritten notes, or heavily degraded scans are hard to manage.

### The impact of prompting on response quality
The system prompt (`AGENT.md`) dictates the AI's behavior and changes the output:
* **Strictness vs. Hallucination:** The current prompt enforces strict adherence to the extracted context (`"Answer ONLY from the context"`). This eliminates hallucinations but makes the AI rigid. If the text says "The device operates at 5V" and the user asks "Can I plug it into a 12V socket?", a strictly prompted AI might say *"I don't know"*, whereas a loosely prompted AI would deduce *"No, it operates at 5V"*.
* **Language translation constraint:** The prompt explicitly instructs the AI to translate context logically into the user's language without sounding robotic, improving the user experience when querying English datasheets in Romanian (or vice versa).

### Current limitations and future improvements

While functional and accurate, the current architecture has architectural limitations that provide room for future enhancement:

* **Limitation 1: Naive chunking strategy**
  * *Issue:* The text splitter cuts text every 1000 characters. It might cut a crucial sentence or paragraph in half, separating a subject from its definition.
  * *Improvement:* Implementing **Semantic Chunking** (splitting by logical sections, headers, or sentences) rather than a fixed character count.
* **Limitation 2: Lack of reranking**
  * *Issue:* The system blindly trusts the top 8 results from ChromaDB based on mathematical distance. Sometimes, chunk #5 is more relevant than chunk #1.
  * *Improvement:* Introducing a **Reranker** model (e.g., Cohere Rerank or BGE-Reranker) before sending the chunks to the LLM.
* **Limitation 3: Layout ignorance**
  * *Issue:* Tesseract OCR extracts raw text but ignores layouts, bold text, graphs, and charts.
  * *Improvement:* Upgrading the pipeline to use multimodal LLMs (passing images directly to the AI)

## How to open

- download archive and double click `ai.bat` from the desktop folder
