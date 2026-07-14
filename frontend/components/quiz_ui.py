"""
StudyMate AI — Quiz Section UI.

Quiz generation, taking, and score review interface.
"""

import streamlit as st

from frontend.utils.api_client import api_client


def render_quiz_page() -> None:
    """Render the quiz section page."""
    st.markdown("""
    <div class="fade-in-up">
        <div class="page-title">📝 Quiz Section</div>
        <div class="page-subtitle">Test your knowledge with AI-generated quizzes</div>
    </div>
    """, unsafe_allow_html=True)

    tab_generate, tab_history = st.tabs(["🎯 Take Quiz", "📋 Quiz History"])

    with tab_generate:
        _render_quiz_generator()

    with tab_history:
        _render_quiz_history()


def _render_quiz_generator() -> None:
    """Render the quiz generation and taking interface."""
    # Generate quiz form
    if not st.session_state.get("current_quiz"):
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 🎯 Generate a Quiz")

        with st.form("quiz_gen_form"):
            topic = st.text_input("Topic", placeholder="e.g., Quadratic Equations, Python Loops, Cell Biology")
            col1, col2 = st.columns(2)
            with col1:
                difficulty = st.selectbox("Difficulty", ["easy", "medium", "hard"], index=1)
            with col2:
                num_questions = st.slider("Number of Questions", 3, 15, 5)

            if st.form_submit_button("🚀 Generate Quiz", use_container_width=True):
                if topic.strip():
                    with st.spinner("🤖 AI is generating your quiz..."):
                        result = api_client.generate_quiz(topic.strip(), difficulty, num_questions)

                    if result.get("success"):
                        import json
                        steps = result["data"].get("agent_steps", [])
                        structured_data = None
                        for step in steps:
                            if step.get("step_type") == "observation" and step.get("tool_name") == "quiz_generator":
                                try:
                                    structured_data = json.loads(step.get("tool_output", "{}"))
                                    break
                                except Exception:
                                    pass
                        
                        st.session_state.current_quiz = {
                            "topic": topic,
                            "difficulty": difficulty,
                            "response": result["data"].get("response", ""),
                            "steps": steps,
                            "structured_data": structured_data,
                        }
                        st.session_state.quiz_answers = {}
                        st.session_state.quiz_submitted = False
                        st.session_state.quiz_results = None
                        st.rerun()
                    else:
                        st.error("Failed to generate quiz. Try again!")
                else:
                    st.warning("Please enter a topic")

        st.markdown('</div>', unsafe_allow_html=True)

    else:
        # Display the generated quiz
        quiz = st.session_state.current_quiz
        structured_data = quiz.get("structured_data")

        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown(f"### 📝 Quiz: {quiz.get('topic', 'Unknown')} ({quiz.get('difficulty', 'medium')})")

        # If we have structured data, render an interactive form
        if structured_data and structured_data.get("questions"):
            questions = structured_data["questions"]

            if not st.session_state.get("quiz_submitted"):
                # Render interactive taking mode
                with st.form("take_quiz_form"):
                    st.markdown(f"*{structured_data.get('instructions', '')}*")
                    
                    for q in questions:
                        q_num = str(q.get("question_number", ""))
                        options = q.get("options", [])
                        question_text = f"**Question {q_num}:** {q.get('question', '')}"
                        
                        # Use radio button for single choice option
                        ans = st.radio(
                            question_text,
                            options=options,
                            key=f"q_ans_{q_num}",
                            index=None, # Starts with no selection
                        )
                        st.session_state.quiz_answers[q_num] = ans
                        st.markdown("---")

                    if st.form_submit_button("🎯 Submit Answers", use_container_width=True):
                        # Ensure all questions answered
                        unanswered = [q_num for q_num, ans in st.session_state.quiz_answers.items() if ans is None]
                        if len(st.session_state.quiz_answers) < len(questions) or unanswered:
                            st.warning("Please answer all questions before submitting!")
                        else:
                            # Find topic id to link progress tracking
                            topic_id = None
                            subjects_res = api_client.get_subjects()
                            if subjects_res.get("success"):
                                for subj in subjects_res.get("data", []):
                                    for t in subj.get("topics", []):
                                        if t["name"].lower().strip() == quiz.get("topic", "").lower().strip():
                                            topic_id = t["id"]
                                            break

                            with st.spinner("Scoring your quiz..."):
                                submit_res = api_client.submit_quiz(
                                    answers=st.session_state.quiz_answers,
                                    quiz_data=structured_data,
                                    topic_id=topic_id,
                                )
                            if submit_res.get("success"):
                                st.session_state.quiz_results = submit_res["data"]
                                st.session_state.quiz_submitted = True
                                st.success("Quiz submitted successfully!")
                                st.rerun()
                            else:
                                st.error("Failed to submit quiz. Please try again.")
            else:
                # Render result mode
                results_data = st.session_state.quiz_results
                if results_data:
                    score_pct = results_data.get("score_percentage", 0)
                    correct_ans = results_data.get("correct_answers", 0)
                    total_q = results_data.get("total_questions", 0)
                    
                    st.markdown(f"#### 🏆 Your Score: **{correct_ans}/{total_q} ({score_pct:.0f}%)**")
                    
                    # Highlight colors
                    if score_pct >= 80:
                        st.success("🌟 Excellent work!")
                    elif score_pct >= 60:
                        st.info("👍 Good job, but keep revising!")
                    else:
                        st.error("📖 Time to study some more!")

                    st.markdown("---")
                    
                    # Show breakdown of answers
                    for q in questions:
                        q_num = str(q.get("question_number", ""))
                        user_ans = st.session_state.quiz_answers.get(q_num, "")
                        correct_ans_val = q.get("correct_answer", "")
                        is_correct = user_ans == correct_ans_val
                        
                        st.markdown(f"**Question {q_num}:** {q.get('question', '')}")
                        
                        for opt in q.get("options", []):
                            if opt == correct_ans_val:
                                st.markdown(f"🟢 **{opt}** *(Correct Answer)*")
                            elif opt == user_ans and not is_correct:
                                st.markdown(f"🔴 **{opt}** *(Your Incorrect Selection)*")
                            else:
                                st.markdown(f"⚪ {opt}")
                                
                        if is_correct:
                            st.markdown("✅ **Correct!**")
                        else:
                            st.markdown("❌ **Incorrect.**")
                            
                        if q.get("explanation"):
                            st.markdown(f"*Explanation:* {q.get('explanation')}")
                        st.markdown("---")
                else:
                    st.warning("No quiz results found.")
        else:
            # Fallback to plain markdown response if structured data not parsed
            st.warning("Note: Interactive mode is unavailable because structured JSON quiz data could not be parsed. Showing raw AI response instead:")
            st.markdown(quiz.get("response", ""))

        st.markdown('</div>', unsafe_allow_html=True)

        # Generate New Quiz / Reset button
        if st.button("🔄 Generate New Quiz", use_container_width=True):
            st.session_state.current_quiz = None
            st.session_state.quiz_answers = {}
            st.session_state.quiz_submitted = False
            st.session_state.quiz_results = None
            st.rerun()


def _render_quiz_history() -> None:
    """Render quiz score history."""
    result = api_client.get_quiz_history()

    if not result.get("success"):
        st.error("Failed to load quiz history")
        return

    history = result.get("data", [])

    if not history:
        st.markdown("""
        <div class="glass-card" style="text-align: center; padding: 40px;">
            <div style="font-size: 3rem;">📝</div>
            <div style="color: #f1f5f9; margin: 8px 0;">No quizzes taken yet</div>
            <div style="color: #94a3b8;">Generate your first quiz to get started!</div>
        </div>
        """, unsafe_allow_html=True)
        return

    for score in history:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)

        pct = score.get("score_percentage", 0)
        total = score.get("total_questions", 0)
        correct = score.get("correct_answers", 0)
        taken_at = score.get("taken_at", "")[:16]

        # Color based on score
        if pct >= 80:
            color = "#10b981"
            emoji = "🌟"
        elif pct >= 60:
            color = "#f59e0b"
            emoji = "👍"
        else:
            color = "#ef4444"
            emoji = "📖"

        st.markdown(f"""
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <span style="font-size: 1.5rem;">{emoji}</span>
                <strong style="color: {color}; font-size: 1.3rem;">{pct:.0f}%</strong>
                <span style="color: #94a3b8;"> — {correct}/{total} correct</span>
            </div>
            <div style="color: #64748b; font-size: 0.85rem;">{taken_at}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)
