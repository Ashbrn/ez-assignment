# utils.py

import os
import fitz  # PyMuPDF
from groq_api import groq_chat
import json

def extract_text(uploaded_file):
    """
    Extract text from uploaded PDF or TXT file
    """
    try:
        if uploaded_file.type == "application/pdf":
            # Extract text from PDF
            pdf_bytes = uploaded_file.read()
            pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
            
            text = ""
            for page_num in range(pdf_document.page_count):
                page = pdf_document[page_num]
                text += page.get_text() + "\n"
            
            pdf_document.close()
            return text.strip()
            
        elif uploaded_file.type == "text/plain":
            # Extract text from TXT file
            return uploaded_file.read().decode('utf-8')
        else:
            return "Unsupported file type. Please upload PDF or TXT files."
            
    except Exception as e:
        return f"Error extracting text: {str(e)}"

def generate_summary(text):
    """
    Generate a summary of the document (≤150 words)
    """
    # Limit text length to avoid token limits
    max_length = 3000
    if len(text) > max_length:
        text = text[:max_length] + "..."
    
    prompt = f"""
    Please provide a concise summary of the following document in exactly 150 words or less. 
    Focus on the main points, key arguments, and important conclusions.
    Make it informative and well-structured.

    Respond in plain text format (NOT JSON). Write a clear, readable summary.

    Document:
    {text}

    Summary (150 words max):
    """
    
    return groq_chat(prompt, temperature=0.3, max_tokens=200)

def ask_anything(text, question):
    """
    Answer any question about the document with justification and relevant snippets
    """
    # Limit text length
    max_length = 2500
    if len(text) > max_length:
        text = text[:max_length] + "..."
    
    prompt = f"""
    Based on the following document, please answer the question clearly and provide justification for your answer.

    Document:
    {text}

    Question: {question}

    Please provide a clear, natural text response (NOT JSON format) that includes:
    1. A direct answer to the question
    2. Justification explaining why this answer is correct based on the document
    3. Quote the exact sentences or phrases from the document that support your answer

    Format your response as:
    **Answer:** [Your direct answer]
    
    **Justification:** [Why this answer is correct]
    
    **Supporting Evidence:** "[Quote exact text from document that supports this answer]"
    """
    
    try:
        response = groq_chat(prompt, temperature=0.2, max_tokens=400)
        
        # Extract supporting evidence for highlighting
        supporting_text = extract_supporting_evidence(response, text)
        
        return response, supporting_text
    except Exception as e:
        # Fallback to simple response if there's an error
        error_response = f"Error processing question: {str(e)}"
        return error_response, []

def extract_supporting_evidence(response, original_text):
    """
    Extract quoted text from the response that can be highlighted in the original document
    """
    try:
        import re
        
        # Look for text in quotes in the response
        quoted_patterns = [
            r'"([^"]+)"',  # Text in double quotes
            r"'([^']+)'",  # Text in single quotes
            r'Supporting Evidence.*?["\']([^"\']+)["\']',  # Text after "Supporting Evidence"
        ]
        
        supporting_snippets = []
        
        for pattern in quoted_patterns:
            try:
                matches = re.findall(pattern, response, re.IGNORECASE | re.DOTALL)
                for match in matches:
                    # Clean up the match
                    clean_match = match.strip()
                    if len(clean_match) > 10 and clean_match.lower() in original_text.lower():
                        supporting_snippets.append(clean_match)
            except Exception:
                continue  # Skip this pattern if it fails
        
        return supporting_snippets[:3]  # Limit to 3 snippets max
    except Exception:
        return []  # Return empty list if anything fails

def extract_key_facts(text):
    """Extract specific facts, numbers, names, and concepts from the document"""
    
    # First, let's extract key information using AI
    extract_prompt = f"""
    Analyze this document and extract specific, factual information that could be used for quiz questions.
    
    Extract:
    1. Specific numbers, dates, percentages, statistics
    2. Names of people, places, organizations, products
    3. Technical terms and their definitions
    4. Key processes, methods, or procedures described
    5. Important facts, findings, or conclusions
    6. Cause-and-effect relationships mentioned
    
    Document:
    {text[:3000]}  # Use first part for extraction
    
    Return the information in this format:
    NUMBERS/DATES: [list specific numbers, dates, percentages found]
    NAMES: [list specific names of people, places, organizations]
    TERMS: [list technical terms and concepts with brief definitions]
    PROCESSES: [list key processes or methods described]
    FACTS: [list important facts or findings]
    RELATIONSHIPS: [list cause-effect or other relationships]
    """
    
    try:
        extraction = groq_chat(extract_prompt, temperature=0.1, max_tokens=800)
        return extraction
    except:
        return "Could not extract key facts"

def challenge_me(text, question_type="mixed"):
    """
    Generate 3 high-quality challenge questions from the document
    question_type: "mcq", "open", or "mixed"
    """
    # First extract key facts from the document
    key_facts = extract_key_facts(text)
    
    # Use a smaller, focused portion of text for question generation
    focused_text = text[:4000] if len(text) > 4000 else text
    
    if question_type == "mcq":
        prompt = f"""
        You are creating quiz questions for students studying this document. Use the extracted key facts to create 3 specific multiple choice questions.

        KEY FACTS EXTRACTED:
        {key_facts}

        DOCUMENT TEXT:
        {focused_text}

        Create 3 MCQ questions that test specific knowledge from this document. Each question MUST:
        1. Reference specific facts, numbers, names, or terms from the extracted key facts
        2. Be answerable ONLY by someone who read this specific document
        3. Have one clearly correct answer and three plausible wrong answers
        4. Test actual learning, not guessing

        EXAMPLE of what I want:
        - If document mentions "Python increased performance by 40%", ask "According to the document, by what percentage did Python increase performance?"
        - If document mentions "Dr. Smith's research", ask "Who conducted the research mentioned in the document?"
        - If document explains "machine learning algorithms", ask "What does the document define machine learning algorithms as?"

        Return ONLY this JSON format:
        [
            {{
                "question": "[Specific question using exact facts from document]",
                "type": "mcq",
                "options": ["A) [correct answer from document]", "B) [plausible wrong answer]", "C) [plausible wrong answer]", "D) [plausible wrong answer]"],
                "correct_answer": "A",
                "explanation": "The document specifically states this fact in the section about [topic]"
            }},
            {{
                "question": "[Another specific question]",
                "type": "mcq",
                "options": ["A) [wrong]", "B) [correct from document]", "C) [wrong]", "D) [wrong]"],
                "correct_answer": "B",
                "explanation": "This information is directly mentioned in the document"
            }},
            {{
                "question": "[Third specific question]",
                "type": "mcq",
                "options": ["A) [wrong]", "B) [wrong]", "C) [correct from document]", "D) [wrong]"],
                "correct_answer": "C",
                "explanation": "The document clearly explains this concept"
            }}
        ]
        """
    elif question_type == "open":
        prompt = f"""
        Create 3 open-ended questions that require students to explain, analyze, or discuss specific content from this document.

        KEY FACTS EXTRACTED:
        {key_facts}

        DOCUMENT TEXT:
        {focused_text}

        Create questions that:
        1. Reference specific concepts, processes, or findings from the document
        2. Ask students to explain HOW or WHY something works based on the document
        3. Require analysis of relationships, causes, effects mentioned in the text
        4. Use exact terms and concepts from the document

        EXAMPLE of what I want:
        - If document explains a process: "Explain the [specific process name] described in the document and analyze why each step is important"
        - If document presents findings: "Analyze the [specific findings] presented in the document and discuss their implications"
        - If document compares things: "Compare [specific items] as described in the document and explain the key differences"

        Return ONLY this JSON format:
        [
            {{
                "question": "Explain [specific concept/process from document] as described in the text and analyze its importance or how it works.",
                "type": "open"
            }},
            {{
                "question": "The document presents [specific findings/data/argument]. Analyze this information and discuss what it means or implies.",
                "type": "open"
            }},
            {{
                "question": "Based on the document's explanation of [specific topic], compare/contrast/evaluate [specific aspects] and explain the significance.",
                "type": "open"
            }}
        ]
        """
    else:  # mixed
        prompt = f"""
        Create exactly 3 questions: 2 multiple choice AND 1 open-ended question using specific facts from this document.

        KEY FACTS EXTRACTED:
        {key_facts}

        DOCUMENT TEXT:
        {focused_text}

        REQUIREMENTS:
        - Questions 1 & 2: "type": "mcq" with 4 options each, testing specific facts
        - Question 3: "type": "open" requiring explanation/analysis
        - ALL questions must use specific information from the extracted key facts
        - NO generic questions that could apply to any document

        Return ONLY this JSON format:
        [
            {{
                "question": "[Specific MCQ question using exact facts/numbers/names from document]",
                "type": "mcq",
                "options": ["A) [correct from document]", "B) [wrong but plausible]", "C) [wrong but plausible]", "D) [wrong but plausible]"],
                "correct_answer": "A",
                "explanation": "The document specifically mentions this fact"
            }},
            {{
                "question": "[Another specific MCQ question using document facts]",
                "type": "mcq",
                "options": ["A) [wrong]", "B) [correct from document]", "C) [wrong]", "D) [wrong]"],
                "correct_answer": "B",
                "explanation": "This is directly stated in the document"
            }},
            {{
                "question": "Explain [specific concept/process from document] and analyze [specific aspect mentioned in text].",
                "type": "open"
            }}
        ]
        """
    
    # Try multiple times with different approaches
    for attempt in range(3):
        try:
            response = groq_chat(prompt, temperature=0.3 + (attempt * 0.2), max_tokens=1200)
            
            # Clean the response to extract JSON
            response = response.strip()
            if '```json' in response:
                response = response.split('```json')[1].split('```')[0]
            elif '```' in response:
                response = response.split('```')[1].split('```')[0]
            
            # Try to find JSON in the response
            import re
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                response = json_match.group()
            
            questions = json.loads(response)
            
            if isinstance(questions, list) and len(questions) >= 3:
                # Validate questions are specific and well-formed
                valid_questions = []
                for q in questions[:3]:
                    if (q.get('question') and q.get('type') and 
                        len(q['question']) > 20 and
                        not any(generic in q['question'].lower() for generic in ['generic', 'general', 'typical', 'common'])):
                        
                        # Additional validation for MCQ questions
                        if q['type'] == 'mcq':
                            if (q.get('options') and len(q['options']) == 4 and 
                                q.get('correct_answer') and q.get('explanation')):
                                valid_questions.append(q)
                        else:  # open questions
                            valid_questions.append(q)
                
                if len(valid_questions) >= 2:  # Accept if at least 2 good questions
                    return valid_questions[:3]
                    
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            continue
    
    # If all attempts fail, create manual questions based on document content
    return create_manual_questions(focused_text, question_type)

def create_manual_questions(text, question_type):
    """Create questions manually by analyzing document content"""
    
    # Extract key information from the text
    sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 30][:20]
    paragraphs = [p.strip() for p in text.split('\n\n') if len(p.strip()) > 50][:10]
    
    # Look for specific patterns
    numbers = []
    names = []
    concepts = []
    
    import re
    
    # Find numbers, percentages, dates
    number_patterns = re.findall(r'\b\d+(?:\.\d+)?%?\b', text)
    numbers.extend(number_patterns[:5])
    
    # Find capitalized words (potential names/concepts)
    cap_words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
    names.extend([w for w in cap_words if len(w) > 3][:10])
    
    # Find quoted terms or technical terms
    quoted = re.findall(r'"([^"]+)"', text)
    concepts.extend(quoted[:5])
    
    if question_type == "mcq":
        questions = []
        
        # Question 1: About a specific number/statistic if found
        if numbers:
            questions.append({
                "question": f"According to the document, what specific figure or measurement is mentioned?",
                "type": "mcq",
                "options": [
                    f"A) {numbers[0]}",
                    f"B) {int(float(numbers[0].replace('%', ''))) + 10 if numbers[0].replace('%', '').replace('.', '').isdigit() else '25'}%",
                    f"C) {int(float(numbers[0].replace('%', ''))) - 5 if numbers[0].replace('%', '').replace('.', '').isdigit() else '15'}%",
                    f"D) {int(float(numbers[0].replace('%', ''))) + 20 if numbers[0].replace('%', '').replace('.', '').isdigit() else '35'}%"
                ],
                "correct_answer": "A",
                "explanation": f"The document specifically mentions {numbers[0]} in the context of the discussion."
            })
        
        # Question 2: About a specific name/concept if found
        if names:
            questions.append({
                "question": f"Which specific term or name is mentioned in the document?",
                "type": "mcq",
                "options": [
                    f"A) {names[0]}",
                    f"B) Alternative Term",
                    f"C) Different Concept",
                    f"D) Other Reference"
                ],
                "correct_answer": "A",
                "explanation": f"The document specifically references {names[0]} in its content."
            })
        
        # Question 3: About document content
        if sentences:
            first_sentence = sentences[0][:80] + "..." if len(sentences[0]) > 80 else sentences[0]
            questions.append({
                "question": "What does the document primarily discuss in its opening section?",
                "type": "mcq",
                "options": [
                    f"A) {first_sentence}",
                    "B) Alternative topic not mentioned",
                    "C) Different subject matter",
                    "D) Unrelated content"
                ],
                "correct_answer": "A",
                "explanation": "This is directly stated in the document's opening section."
            })
        
        # Fill remaining slots if needed
        while len(questions) < 3:
            questions.append({
                "question": f"Based on the document content, what type of information is primarily presented?",
                "type": "mcq",
                "options": [
                    "A) Detailed explanations and analysis",
                    "B) Simple definitions only",
                    "C) Historical dates and events",
                    "D) Mathematical formulas"
                ],
                "correct_answer": "A",
                "explanation": "The document provides detailed information and explanations about its topic."
            })
        
        return questions[:3]
    
    else:  # open questions
        questions = []
        
        if concepts:
            questions.append({
                "question": f"Explain the concept of '{concepts[0]}' as described in the document and discuss its significance.",
                "type": "open"
            })
        
        if paragraphs:
            main_topic = paragraphs[0][:100] + "..." if len(paragraphs[0]) > 100 else paragraphs[0]
            questions.append({
                "question": f"Analyze the main topic discussed in the document and explain its key components and implications.",
                "type": "open"
            })
        
        questions.append({
            "question": "Based on the information presented in the document, what are the most important takeaways and how might they be applied?",
            "type": "open"
        })
        
        return questions[:3]