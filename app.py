import streamlit as st
from typing import Text, List
import openai
import tiktoken
import os

st.set_page_config(
    layout="wide"
)

openai.api_key = os.getenv("OPENAI_API_KEY")
encoding = tiktoken.get_encoding("cl100k_base")


def find_answers(input_text: Text, questions: List[Text]) -> Text:
    """Return response for each question from LLM."""
    bar = st.progress(0, text="Processing questions...")
    answers = []
    for i, question in enumerate(questions):
        # Set prompt and fill context and question.
        prompt = (
            "Answer the following question using only the provided context. "
            "Do not give any answer that does not come from the context. "
            "If there is not an answer in the context, respond with the text 'out of scope'.\n\n"
            f"CONTEXT:\n{input_text}\n\n"
            f"QUESTION:\n{question}"
        )

        # Check prompt length to determine appropriate model.
        prompt_len = len(encoding.encode(prompt))
        if prompt_len < 3000:
            model = "gpt-3.5-turbo"
        else:
            model = "gpt-3.5-turbo-16k"

        # Query ChatGPT for answer.
        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=[{"role": "system", "content": prompt}]
            )
            answer = response["choices"][0]["message"]["content"]
        except:
            # Retry ChatGPT call if the first call times out or fails.
            try:
                response = openai.ChatCompletion.create(
                    model=model,
                    messages=[{"role": "system", "content": prompt}]
                )
                answer = response["choices"][0]["message"]["content"]
            except:
                answer = "Oops, unable to get answer from ChatGPT!"

        answers.append(answer)
        bar.progress((i + 1) / len(questions), text=f"Processing question {i + 1}/{len(questions)}...")

    return answers


st.title("Question Answering")

# Collect input variables from Streamlit frontend.
form = st.form("form")
para_col, ques_col = form.columns(2)
with para_col:
    input_text = form.text_area(
        "Enter paragraph input text:"
    )
with ques_col:
    all_questions = form.text_area(
        "Enter questions, one per line:"
    )
submit = form.form_submit_button(
    "Submit"
)

if submit:
    # Retrieve answers.
    questions = all_questions.split("\n")
    answers = find_answers(input_text, questions)

    # Write question-answer pairs to Streamlit frontend.
    for i in range(len(questions)):
        st.write(f"Question: {questions[i]}")
        st.write(f"Answer: {answers[i]}")
        st.write("---")
