import os
from groq import Groq
from database import db 

groq_key = os.getenv("GROQ_API_KEY")
groq_client = Groq(api_key=groq_key)

def read_agent_instructions():
    file_path = "AGENT.md"
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "You are a strict assistant. Answer only from the context."

def get_page_ranges(pages_set):
    if not pages_set:
        return ""
    
    valid_pages = [p for p in pages_set if isinstance(p, int)]
    if not valid_pages:
        return ""

    sorted_pages = sorted(valid_pages)
    ranges = []
    start = sorted_pages[0]
    end = sorted_pages[0]

    for p in sorted_pages[1:]:
        if p == end + 1:
            end = p
        else:
            if start == end:
                ranges.append(str(start))
            else:
                ranges.append(f"{start}-{end}")
            start = p
            end = p
      
    if start == end:
        ranges.append(str(start))
    else:
        ranges.append(f"{start}-{end}")

    return ", ".join(ranges)

def ask_agent(user_question, history=[]):
    search_query = user_question
    
    if len(history) > 0:
        last_ai_message = next((msg['text'] for msg in reversed(history) if msg['role'] == 'assistant'), "")
        if last_ai_message:
            context_subject = last_ai_message[:100].strip()
            search_query = f"{context_subject} {user_question}"
        else:
            last_user_message = history[-1]['text']
            search_query = f"{last_user_message} {user_question}"

    results = db.similarity_search(search_query, k=8)
    
    extracted_context = ""

    source_dict = {} 
    
    for chunk in results:
        filename = chunk.metadata.get('source', 'Unknown').split('/')[-1].split('\\')[-1]
        raw_page = chunk.metadata.get('page', None)
        
        page = None
        if isinstance(raw_page, int):
            page = raw_page + 1
        elif isinstance(raw_page, str) and raw_page.isdigit():
            page = int(raw_page) + 1
            
        page_info = f", Page: {page}" if page else ""
        extracted_context += f"[Source: {filename}{page_info}]\n{chunk.page_content}\n\n"
        
        if filename not in source_dict:
            source_dict[filename] = set()
        if page is not None:
            source_dict[filename].add(page)
            
    formatted_sources = []
    for file, pages in source_dict.items():
        if pages:
            page_str = get_page_ranges(pages)
            prefix = "Page" if "," not in page_str and "-" not in page_str else "Pages"
            formatted_sources.append(f"{file} ({prefix} {page_str})")
        else:
            formatted_sources.append(file)
    
    system_message = read_agent_instructions()
    groq_messages = [{"role": "system", "content": system_message}]
    
    for msg in history:
        groq_messages.append({"role": msg['role'], "content": msg['text']})
        
    final_prompt = f"""
    Extracted context from documentation:
    ---
    {extracted_context}
    ---
    
    Current question: {user_question}
    Answer:
    """
    groq_messages.append({"role": "user", "content": final_prompt})
    
    response = groq_client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=groq_messages,
        temperature=0.1
    )
    
    response_text = response.choices[0].message.content
    
    if "i could not find information" in response_text.lower() or "nu am găsit informații" in response_text.lower():
        formatted_sources = []
        
    if "[NO_SOURCES]" in response_text:
        formatted_sources = [] 
        response_text = response_text.replace("[NO_SOURCES]", "").strip() 

    return {
        "response": response_text,
        "sources": formatted_sources 
    }