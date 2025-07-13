# app.py

import streamlit as st
from utils import extract_text, generate_summary, ask_anything, challenge_me
from groq_api import groq_chat, test_groq_connection

st.set_page_config(page_title="Smart Assistant", layout="wide")

# Initialize session state for chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "document_text" not in st.session_state:
    st.session_state.document_text = ""
if "input_key" not in st.session_state:
    st.session_state.input_key = 0

st.title("🧠 Smart Assistant for Research Summarization")

# Custom CSS for better chat styling
st.markdown("""
<style>
    .chat-container {
        max-height: 400px;
        overflow-y: auto;
        padding: 10px;
        border: 1px solid #333;
        border-radius: 10px;
        background-color: #0e1117;
    }
    .user-message {
        background-color: #2b313e;
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
        margin-left: 20%;
        color: white;
    }
    .assistant-message {
        background-color: #1e1e1e;
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
        margin-right: 20%;
        color: white;
    }
    .stTextInput > div > div > input {
        background-color: #2b313e;
        color: white;
        border: 1px solid #444;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.header("📄 Upload Document")

# Connection status
if "connection_tested" not in st.session_state:
    st.session_state.connection_tested = False
    st.session_state.connection_status = None

if not st.session_state.connection_tested:
    with st.sidebar:
        with st.spinner("🔍 Testing API connection..."):
            st.session_state.connection_status = test_groq_connection()
            st.session_state.connection_tested = True

# Show connection status
if st.session_state.connection_status:
    st.sidebar.success("🟢 API Connection: Active")
else:
    st.sidebar.error("🔴 API Connection: Issues detected")
    st.sidebar.info("💡 The app may work with limited functionality")

uploaded_file = st.sidebar.file_uploader("Upload a PDF or TXT file", type=["pdf", "txt"])

if uploaded_file:
    # Text extraction
    raw_text = extract_text(uploaded_file)
    st.session_state.document_text = raw_text
    st.success("✅ Document uploaded and text extracted successfully!")

    # Document preview in sidebar
    with st.sidebar.expander("📖 Document Preview"):
        preview_text = raw_text[:500] + "..." if len(raw_text) > 500 else raw_text
        st.text_area("Document content:", preview_text, height=150, disabled=True)
    
    st.sidebar.markdown("### 🤖 Choose a Mode")
    mode = st.sidebar.radio("Select interaction mode:", ["Summary", "Ask Anything", "Challenge Me"])

    # Summary
    if mode == "Summary":
        st.subheader("📑 Document Summary")
        summary = generate_summary(raw_text)
        st.text_area("Generated Summary (≤150 words):", summary, height=200)

    # Ask Anything - Chat Interface
    elif mode == "Ask Anything":
        st.subheader("💬 Chat About the Document")
        
        # Display chat history
        chat_container = st.container()
        with chat_container:
            for i, message in enumerate(st.session_state.chat_history):
                if message["role"] == "user":
                    st.markdown(f"""
                    <div style="background-color: #2b313e; padding: 10px; border-radius: 10px; margin: 5px 0; margin-left: 20%;">
                        <strong>You:</strong> {message["content"]}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="background-color: #1e1e1e; padding: 10px; border-radius: 10px; margin: 5px 0; margin-right: 20%;">
                        <strong>🤖 Assistant:</strong> {message["content"]}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Show supporting snippets if available
                    if "supporting_snippets" in message and message["supporting_snippets"]:
                        with st.expander("📄 Supporting Evidence from Document"):
                            for i, snippet in enumerate(message["supporting_snippets"], 1):
                                st.markdown(f"""
                                <div style="background-color: #2d2d2d; padding: 8px; border-left: 3px solid #4CAF50; margin: 5px 0;">
                                    <strong>Evidence {i}:</strong><br>
                                    <em>"{snippet}"</em>
                                </div>
                                """, unsafe_allow_html=True)
        
        # Chat input with Enter key support using form
        with st.form(key=f"chat_form_{st.session_state.input_key}", clear_on_submit=True):
            col1, col2 = st.columns([4, 1])
            with col1:
                user_question = st.text_input(
                    "Ask a question about the document:", 
                    placeholder="Type your question here and press Enter or click Send...",
                    key=f"question_input_{st.session_state.input_key}"
                )
            with col2:
                send_button = st.form_submit_button("Send")
        
        # Clear chat button
        if st.button("🗑️ Clear Chat"):
            st.session_state.chat_history = []
            st.session_state.input_key += 1  # Reset input field
            st.rerun()
        
        # Process new message (works with both Enter key and Send button)
        if send_button and user_question.strip():
            # Add user message to history
            st.session_state.chat_history.append({"role": "user", "content": user_question})
            
            # Get AI response
            with st.spinner("🤖 Thinking..."):
                response, supporting_snippets = ask_anything(st.session_state.document_text, user_question)
            
            # Add AI response to history
            st.session_state.chat_history.append({
                "role": "assistant", 
                "content": response,
                "supporting_snippets": supporting_snippets
            })
            
            # Clear the input by incrementing the key
            st.session_state.input_key += 1
            st.rerun()

    # Challenge Me
    elif mode == "Challenge Me":
        st.subheader("🧠 Challenge Me")
        
        # Question type selector
        col1, col2 = st.columns([2, 1])
        with col1:
            question_type = st.selectbox(
                "Choose question type:",
                ["Mixed (MCQ + Open)", "Multiple Choice Only", "Open-ended Only"],
                key="question_type_selector"
            )
        with col2:
            if st.button("🎯 Start New Challenge", key="start_challenge"):
                # Map selection to function parameter
                type_mapping = {
                    "Mixed (MCQ + Open)": "mixed",
                    "Multiple Choice Only": "mcq", 
                    "Open-ended Only": "open"
                }
                selected_type = type_mapping[question_type]
                
                # Generate questions and store in session state
                st.session_state.challenge_questions = challenge_me(st.session_state.document_text, selected_type)
                st.session_state.challenge_answers = {}
                st.session_state.challenge_feedback = {}
                st.rerun()
        
        # Display questions if they exist
        if "challenge_questions" in st.session_state and st.session_state.challenge_questions:
            st.markdown("---")
            total_score = 0
            max_score = 0
            
            for idx, q in enumerate(st.session_state.challenge_questions, 1):
                st.markdown(f"### Question {idx}")
                st.markdown(f"**{q['question']}**")
                
                if q.get('type') == 'mcq':
                    # Multiple Choice Question
                    options = q.get('options', [])
                    user_choice = st.radio(
                        f"Select your answer for Q{idx}:",
                        options,
                        key=f"mcq_{idx}",
                        index=None
                    )
                    
                    if user_choice:
                        # Extract letter from choice (A, B, C, D)
                        selected_letter = user_choice[0] if user_choice else ""
                        correct_answer = q.get('correct_answer', 'A')
                        
                        if selected_letter == correct_answer:
                            st.success("✅ Correct!")
                            st.info(f"**Explanation:** {q.get('explanation', 'Good job!')}")
                            total_score += 10
                        else:
                            st.error(f"❌ Incorrect. The correct answer is {correct_answer}")
                            st.info(f"**Explanation:** {q.get('explanation', 'Better luck next time!')}")
                        max_score += 10
                
                else:
                    # Open-ended Question
                    user_answer = st.text_area(
                        f"Your answer for Q{idx}:",
                        key=f"open_{idx}",
                        height=100,
                        placeholder="Type your detailed answer here..."
                    )
                    
                    if user_answer and st.button(f"📝 Evaluate Q{idx}", key=f"eval_{idx}"):
                        with st.spinner("🤖 Evaluating your answer..."):
                            eval_prompt = f"""
                            Evaluate this answer for the given question. Provide a score out of 10 and detailed feedback.
                            
                            Question: {q['question']}
                            Student Answer: {user_answer}
                            
                            Please provide:
                            1. Score out of 10
                            2. What was good about the answer
                            3. What could be improved
                            4. Key points that were missed (if any)
                            
                            Format: Score: X/10
                            Feedback: [detailed feedback]
                            """
                            
                            eval_response = groq_chat(eval_prompt, temperature=0.3, max_tokens=300)
                            st.session_state.challenge_feedback[f"q{idx}"] = eval_response
                            st.rerun()
                    
                    # Display feedback if available
                    if f"q{idx}" in st.session_state.challenge_feedback:
                        st.markdown("**🤖 AI Evaluation:**")
                        st.write(st.session_state.challenge_feedback[f"q{idx}"])
                        max_score += 10
                
                st.markdown("---")
            
            # Show overall score for MCQ questions
            if max_score > 0:
                score_percentage = (total_score / max_score) * 100
                st.markdown(f"### 📊 Current Score: {total_score}/{max_score} ({score_percentage:.1f}%)")
                
                if score_percentage >= 80:
                    st.success("🎉 Excellent work!")
                elif score_percentage >= 60:
                    st.info("👍 Good job!")
                else:
                    st.warning("📚 Keep studying!")
        
        else:
            st.info("👆 Click 'Start New Challenge' to begin!")
            st.markdown("""
            **Challenge Types:**
            - **Mixed**: 2 Multiple Choice + 1 Open-ended question
            - **Multiple Choice**: 3 MCQ questions with instant feedback
            - **Open-ended**: 3 analytical questions requiring detailed answers
            """)

# Handle case when no document is uploaded
else:
    st.info("👆 Please upload a PDF or TXT document to get started!")
    st.markdown("""
    ### How to use this Smart Assistant:
    
    1. **📄 Upload Document**: Use the sidebar to upload a PDF or TXT file
    2. **📑 Summary**: Get a concise summary of your document
    3. **💬 Ask Anything**: Chat with the AI about your document content
    4. **🧠 Challenge Me**: Test your understanding with AI-generated questions
    
    The assistant will analyze your document and provide intelligent responses based on the content.
    """)
