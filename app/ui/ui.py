import streamlit as st
from app.logic.extractor import extract_tables_from_pdf
from app.logic.cleaner import clean_bob_data, clean_ricb_data

def load_css(file_path="app/ui/style.css"):
    with open(file_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def render_ui():
    st.set_page_config(layout="wide")
    load_css()
    st.title("📊 AI Reconciliation System with Chat Support")

    if "match_started" not in st.session_state:
        st.session_state.match_started = False
    if "chat_open" not in st.session_state:
        st.session_state.chat_open = False

    # Toggle chat state manually
    if st.query_params.get("toggle_chat"):
     st.session_state.chat_open = not st.session_state.chat_open


    # Display chatbot panel if opened
    if st.session_state.chat_open:
        with st.container():
            st.markdown("### 🤖 Smart Chat Assistant")
            st.info("This space will be used for chatting about uploaded files.")
            st.markdown("➡️ Use this to query policies, summaries, and more (coming soon).")
        return

    # Sidebar for file uploads
    with st.sidebar:
        st.header("📂 Upload Files")
        bob_file = st.file_uploader("Upload BOB PDF", type=["pdf"], key="bob_pdf")
        ricb_file = st.file_uploader("Upload RICBL PDF", type=["pdf"], key="ricb_pdf")

    if not bob_file or not ricb_file:
        st.info("⬅️ Please upload both BOB and RICBL PDF files to continue.")
    else:
        bob_raw_df = extract_tables_from_pdf(bob_file)
        ricb_raw_df = extract_tables_from_pdf(ricb_file)
        bob_df = clean_bob_data(bob_raw_df)
        ricb_df = clean_ricb_data(ricb_raw_df)

        view = st.radio("🔀 Select View Mode", ["📄 Raw Data", "🧹 Cleaned Tables", "🔁 Exact Matching"], horizontal=True)

        if view == "📄 Raw Data":
            st.subheader("📄 Raw Extracted Tables")
            st.markdown("### 🧾 BOB Raw Table")
            st.dataframe(bob_raw_df, use_container_width=True)
            st.markdown("### 🧾 RICBL Raw Table")
            st.dataframe(ricb_raw_df, use_container_width=True)

        elif view == "🧹 Cleaned Tables":
            st.subheader("🧹 Cleaned Tables")
            st.markdown("### ✅ BOB Cleaned Table")
            st.dataframe(bob_df, use_container_width=True)
            st.markdown("### ✅ RICBL Cleaned Table")
            st.dataframe(ricb_df, use_container_width=True)

        elif view == "🔁 Exact Matching":
            st.subheader("🔁 Exact Matching Options")
            col1, col2 = st.columns(2)
            with col1:
                bob_match_col = st.selectbox("🔷 Select BOB Column to Match", bob_df.columns.tolist())
            with col2:
                ricb_match_col = st.selectbox("🔶 Select RICBL Column to Match", ricb_df.columns.tolist())

            if st.button("▶️ Start Matching"):
                st.session_state.match_started = True
                st.session_state.bob_match_col = bob_match_col
                st.session_state.ricb_match_col = ricb_match_col

            if st.session_state.match_started:
                matched = bob_df[bob_df[st.session_state.bob_match_col].isin(ricb_df[st.session_state.ricb_match_col])]
                unmatched_bob = bob_df[~bob_df[st.session_state.bob_match_col].isin(ricb_df[st.session_state.ricb_match_col])]
                unmatched_ricb = ricb_df[~ricb_df[st.session_state.ricb_match_col].isin(bob_df[st.session_state.bob_match_col])]

                st.subheader("📊 Reconciliation Summary")
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.markdown(f"<div class='stat-card blue'><h3>🔷 BOB Total</h3><h2>{len(bob_df)}</h2></div>", unsafe_allow_html=True)
                with c2:
                    st.markdown(f"<div class='stat-card orange'><h3>🔶 RICBL Total</h3><h2>{len(ricb_df)}</h2></div>", unsafe_allow_html=True)
                with c3:
                    st.markdown(f"<div class='stat-card green'><h3>✅ Matched</h3><h2>{len(matched)}</h2></div>", unsafe_allow_html=True)

                c4, c5 = st.columns(2)
                with c4:
                    st.markdown(f"<div class='stat-card red'><h3>❌ Unmatched in BOB</h3><h2>{len(unmatched_bob)}</h2></div>", unsafe_allow_html=True)
                with c5:
                    st.markdown(f"<div class='stat-card red'><h3>❌ Unmatched in RICBL</h3><h2>{len(unmatched_ricb)}</h2></div>", unsafe_allow_html=True)

                with st.expander("✅ Matched Records"):
                    st.dataframe(matched, use_container_width=True)

                with st.expander("❌ Unmatched BOB Records"):
                    st.dataframe(unmatched_bob, use_container_width=True)

                with st.expander("❌ Unmatched RICBL Records"):
                    st.dataframe(unmatched_ricb, use_container_width=True)

    # Floating Chat Button as HTML (always visible)
    st.markdown("""
        <style>
            #chat-float-btn {
                position: fixed;
                bottom: 30px;
                right: 30px;
                background-color: #4CAF50;
                color: white;
                font-size: 22px;
                padding: 14px 18px;
                border-radius: 50%;
                border: none;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
                animation: pulse 2s infinite;
                z-index: 9999;
                cursor: pointer;
            }

            @keyframes pulse {
                0% { transform: scale(1); }
                50% { transform: scale(1.1); }
                100% { transform: scale(1); }
            }
        </style>
        <script>
            const toggleChat = () => {
                const url = new URL(window.location.href);
                url.searchParams.set("toggle_chat", "true");
                window.location.href = url.toString();
            }
        </script>
        <button id="chat-float-btn" onclick="toggleChat()">💬</button>
    """, unsafe_allow_html=True)