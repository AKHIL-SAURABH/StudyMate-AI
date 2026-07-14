"""
StudyMate AI — Chat UI.

Conversational interface for the AI study mentor
with message history and agent reasoning visibility.
"""

import streamlit as st

from frontend.utils.api_client import api_client


def render_chat_page() -> None:
    """Render the AI chat page."""
    st.markdown("""
    <div class="fade-in-up">
        <div class="page-title">💬 AI Study Mentor</div>
        <div class="page-subtitle">Ask me anything about your studies — I'll reason, use tools, and give you the best advice!</div>
    </div>
    """, unsafe_allow_html=True)

    # Load chat history from DB if session state messages are empty
    if not st.session_state.get("chat_messages"):
        history_result = api_client.get_chat_history()
        if history_result.get("success"):
            history_data = history_result.get("data", [])
            messages = []
            for msg in reversed(history_data):
                messages.append({
                    "role": msg.get("role"),
                    "content": msg.get("content"),
                })
            st.session_state.chat_messages = messages
            if history_data:
                st.session_state.conversation_id = history_data[0].get("conversation_id")

    # Settings row
    col1, col2 = st.columns([3, 1])
    with col2:
        show_steps = st.toggle("Show Agent Reasoning", key="show_agent_steps")

    # Chat container
    chat_container = st.container()

    with chat_container:
        # Display message history
        for msg in st.session_state.get("chat_messages", []):
            role = msg.get("role", "user")
            content = msg.get("content", "")

            if role == "user":
                st.markdown(f"""
                <div class="chat-user">
                    <strong>🧑‍🎓 You:</strong><br>{content}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-assistant">
                    <strong>🎓 StudyMate AI:</strong><br>{content}
                </div>
                """, unsafe_allow_html=True)

                # Show agent steps if enabled
                if show_steps and msg.get("steps"):
                    with st.expander("🔍 Agent Reasoning Steps", expanded=False):
                        for step in msg["steps"]:
                            step_type = step.get("step_type", "")
                            step_content = step.get("content", "")

                            if step_type == "thought":
                                st.markdown(f"💭 **Thought:** {step_content}")
                            elif step_type == "action":
                                st.markdown(f"⚡ **Action:** {step_content}")
                                if step.get("tool_name"):
                                    st.code(f"Tool: {step['tool_name']}\nInput: {step.get('tool_input', {})}", language="json")
                            elif step_type == "observation":
                                st.markdown(f"👁️ **Observation:** {step_content[:300]}...")
                            elif step_type == "reflection":
                                st.markdown(f"🪞 **Reflection:** {step_content}")
                            elif step_type == "final":
                                st.markdown("✅ **Final Answer Generated**")

                            st.markdown("---")

                # Show tools used
                if msg.get("tools_used"):
                    tools_text = ", ".join(msg["tools_used"])
                    st.markdown(f"""
                    <div style="color: #64748b; font-size: 0.8rem; padding: 4px 12px;">
                        🔧 Tools used: {tools_text}
                    </div>
                    """, unsafe_allow_html=True)

    # Chat input
    st.markdown("<br>", unsafe_allow_html=True)

    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_area(
            "Message",
            placeholder="Ask me about study plans, quizzes, progress, or anything study-related...",
            height=100,
            key="chat_input",
            label_visibility="collapsed",
        )

        col1, col2, col3 = st.columns([1, 1, 4])
        with col1:
            submitted = st.form_submit_button("📤 Send", use_container_width=True)
        with col2:
            if st.form_submit_button("🗑️ Clear Chat", use_container_width=True):
                st.session_state.chat_messages = []
                st.session_state.conversation_id = None
                st.rerun()

    if submitted and user_input.strip():
        # Add user message
        st.session_state.chat_messages.append({
            "role": "user",
            "content": user_input.strip(),
        })

        # Send to API
        with st.spinner("🤔 Thinking... (The AI is reasoning, selecting tools, and reflecting)"):
            result = api_client.send_message(
                message=user_input.strip(),
                conversation_id=st.session_state.get("conversation_id"),
            )

        if result.get("success"):
            data = result["data"]
            st.session_state.conversation_id = data.get("conversation_id")

            st.session_state.chat_messages.append({
                "role": "assistant",
                "content": data.get("response", ""),
                "steps": data.get("agent_steps", []),
                "tools_used": data.get("tools_used", []),
            })
        else:
            error = result.get("error", {})
            st.session_state.chat_messages.append({
                "role": "assistant",
                "content": f"❌ Error: {error.get('message', 'Something went wrong')}",
            })

        st.rerun()

    # Suggestion chips
    st.markdown("#### 💡 Try asking:")
    suggestions = [
        "Create a study plan for my Math exam next month",
        "What are my weakest topics?",
        "Generate a quiz about Python programming",
        "How much time do I need to study Physics?",
        "Give me some motivation to study",
        "Show me my study statistics",
    ]

    cols = st.columns(3)
    for i, suggestion in enumerate(suggestions):
        with cols[i % 3]:
            if st.button(suggestion, key=f"suggest_{i}", use_container_width=True):
                st.session_state.chat_messages.append({"role": "user", "content": suggestion})

                with st.spinner("🤔 Thinking..."):
                    result = api_client.send_message(
                        message=suggestion,
                        conversation_id=st.session_state.get("conversation_id"),
                    )

                if result.get("success"):
                    data = result["data"]
                    st.session_state.conversation_id = data.get("conversation_id")
                    st.session_state.chat_messages.append({
                        "role": "assistant",
                        "content": data.get("response", ""),
                        "steps": data.get("agent_steps", []),
                        "tools_used": data.get("tools_used", []),
                    })
                else:
                    error = result.get("error", {})
                    st.session_state.chat_messages.append({
                        "role": "assistant",
                        "content": f"❌ Error: {error.get('message', 'Something went wrong')}",
                    })

                st.rerun()
