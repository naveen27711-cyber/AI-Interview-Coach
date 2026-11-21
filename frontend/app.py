
import streamlit as st
import requests

API_URL = "https://ai-interview-coach-4i7d.onrender.com"

st.title("AI Interview Coach")

# Initialize session state
st.session_state.setdefault("started", False)
st.session_state.setdefault("finished", False)

# Start Interview screen
if not st.session_state["started"]:

    role = st.text_input("Target Job Role")

    experience = st.selectbox(
        "Experience Level",
        ["Fresher", "1-3 years", "3+ years"]
    )

    if st.button("Start Interview"):

        if not role.strip():
            st.warning("Please enter your target job role.")

        else:
            payload = {
                "role": role,
                "experience": experience
            }

            try:
                res = requests.post(
                    f"{API_URL}/interviews",
                    json=payload,
                    timeout=120
                )

                if res.status_code == 200:
                    data = res.json()

                    st.session_state["session_id"] = data["session_id"]
                    st.session_state["question"] = data["question"]
                    st.session_state["started"] = True
                    st.rerun()

                else:
                    # backend error message .........
                    st.error(res.json().get("detail", "Something went wrong."))

            except requests.exceptions.ConnectionError:
                st.error("Backend is not running. Start FastAPI first.")

            except requests.exceptions.Timeout:
                st.error("Request timed out. Please try again.")


# Interview screen
if st.session_state["started"] and not st.session_state["finished"]:

    st.subheader("Interview Question")
    st.write(st.session_state["question"])

    answer = st.text_area("Your Answer", max_chars=400)

    if st.button("Submit Answer"):

        if not answer.strip():
            st.warning("Please enter your answer.")

        else:
            session_id = st.session_state["session_id"]
            payload = {"answer": answer}

            try:
                res = requests.post(
                    f"{API_URL}/interviews/{session_id}/answer",
                    json=payload,
                    timeout=120
                )

                if res.status_code == 200:
                    data = res.json()

                    if "summary" in data:
                        st.session_state["summary"] = data["summary"]
                        st.session_state["scores"] = data["scores"]
                        st.session_state["finished"] = True

                    else:
                        st.session_state["question"] = data["question"]
                        st.session_state["evaluation"] = data["evaluation"]

                    st.rerun()

                else:
                    st.error(res.json().get("detail", "Something went wrong. Please try again."))

            except requests.exceptions.ConnectionError:
                st.error("Backend connection failed.")

            except requests.exceptions.Timeout:
                st.error("Request timed out.")


# Evaluation display
if "evaluation" in st.session_state:

    st.subheader("Previous Answer Evaluation")

    st.metric(
        "Score",
        f"{st.session_state['evaluation']['score']}/10"
    )

    st.write(st.session_state["evaluation"]["feedback"])


# Final summary screen
if st.session_state["finished"]:

    st.subheader("Interview Completed!")

    st.metric(
        "Average Score",
        f"{st.session_state['summary']['average_score']}/10"
    )

    st.info(st.session_state["summary"]["message"])


    if st.button("Start New Interview"):

        st.session_state.clear()
        st.rerun()
