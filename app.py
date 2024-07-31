import streamlit as st
import os
from typing import List, Union
from openai import OpenAI
from dotenv import load_dotenv

# Load the environment variables
load_dotenv()
client = OpenAI(
    base_url="https://td.nchc.org.tw/api/v1",
    api_key=os.getenv("TAIDE_API_KEY"),)

MAX_TOKENS_PER_CHUNK = 1000

def get_completion(
    prompt: str,
    system_message: str = "You are a helpful assistant.",
    model: str = "taide-llama2-70b",
    temperature: float = 0.3,
    json_mode: bool = False,
) -> Union[str, dict]:
    if json_mode:
        response = client.chat.completions.create(
            model=model,
            temperature=temperature,
            top_p=1,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content
    else:
        response = client.chat.completions.create(
            model=model,
            temperature=temperature,
            top_p=1,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content

def one_chunk_initial_translation(source_lang: str, target_lang: str, source_text: str) -> str:
    system_message = f"You are an expert linguist, specializing in translation from {source_lang} to {target_lang}."
    translation_prompt = f"""This is an {source_lang} to {target_lang} translation, please provide the {target_lang} translation for this text. \
Do not provide any explanations or text apart from the translation.
{source_lang}: {source_text}

{target_lang}:"""
    translation = get_completion(translation_prompt, system_message=system_message)
    return translation

def one_chunk_reflect_on_translation(source_lang: str, target_lang: str, source_text: str, translation_1: str, country: str = "") -> str:
    system_message = f"You are an expert linguist specializing in translation from {source_lang} to {target_lang}. \
You will be provided with a source text and its translation and your goal is to improve the translation."
    if country != "":
        reflection_prompt = f"""Your task is to carefully read a source text and a translation from {source_lang} to {target_lang}, and then give constructive criticism and helpful suggestions to improve the translation. \
The final style and tone of the translation should match the style of {target_lang} colloquially spoken in {country}.

The source text and initial translation, delimited by XML tags <SOURCE_TEXT></SOURCE_TEXT> and <TRANSLATION></TRANSLATION>, are as follows:

<SOURCE_TEXT>
{source_text}
</SOURCE_TEXT>

<TRANSLATION>
{translation_1}
</TRANSLATION>

When writing suggestions, pay attention to whether there are ways to improve the translation's \n\
(i) accuracy (by correcting errors of addition, mistranslation, omission, or untranslated text),\n\
(ii) fluency (by applying {target_lang} grammar, spelling and punctuation rules, and ensuring there are no unnecessary repetitions),\n\
(iii) style (by ensuring the translations reflect the style of the source text and take into account any cultural context),\n\
(iv) terminology (by ensuring terminology use is consistent and reflects the source text domain; and by only ensuring you use equivalent idioms {target_lang}).\n\

Write a list of specific, helpful and constructive suggestions for improving the translation.
Each suggestion should address one specific part of the translation.
Output only the suggestions and nothing else."""
    else:
        reflection_prompt = f"""Your task is to carefully read a source text and a translation from {source_lang} to {target_lang}, and then give constructive criticisms and helpful suggestions to improve the translation. \

The source text and initial translation, delimited by XML tags <SOURCE_TEXT></SOURCE_TEXT> and <TRANSLATION></TRANSLATION>, are as follows:

<SOURCE_TEXT>
{source_text}
</SOURCE_TEXT>

<TRANSLATION>
{translation_1}
</TRANSLATION>

When writing suggestions, pay attention to whether there are ways to improve the translation's \n\
(i) accuracy (by correcting errors of addition, mistranslation, omission, or untranslated text),\n\
(ii) fluency (by applying {target_lang} grammar, spelling and punctuation rules, and ensuring there are no unnecessary repetitions),\n\
(iii) style (by ensuring the translations reflect the style of the source text and take into account any cultural context),\n\
(iv) terminology (by ensuring terminology use is consistent and reflects the source text domain; and by only ensuring you use equivalent idioms {target_lang}).\n\

Write a list of specific, helpful and constructive suggestions for improving the translation.
Each suggestion should address one specific part of the translation.
Output only the suggestions and nothing else."""
    reflection = get_completion(reflection_prompt, system_message=system_message)
    return reflection

def one_chunk_improve_translation(source_lang: str, target_lang: str, source_text: str, translation_1: str, reflection: str) -> str:
    system_message = f"You are an expert linguist, specializing in translation editing from {source_lang} to {target_lang}."
    prompt = f"""Your task is to carefully read, then edit, a translation from {source_lang} to {target_lang}, taking into
account a list of expert suggestions and constructive criticisms.

The source text, the initial translation, and the expert linguist suggestions are delimited by XML tags <SOURCE_TEXT></SOURCE_TEXT>, <TRANSLATION></TRANSLATION> and <EXPERT_SUGGESTIONS></EXPERT_SUGGESTIONS> \
as follows:

<SOURCE_TEXT>
{source_text}
</SOURCE_TEXT>

<TRANSLATION>
{translation_1}
</TRANSLATION>

<EXPERT_SUGGESTIONS>
{reflection}
</EXPERT_SUGGESTIONS>

Please take into account the expert suggestions when editing the translation. Edit the translation by ensuring:

(i) accuracy (by correcting errors of addition, mistranslation, omission, or untranslated text),
(ii) fluency (by applying {target_lang} grammar, spelling and punctuation rules and ensuring there are no unnecessary repetitions), \
(iii) style (by ensuring the translations reflect the style of the source text)
(iv) terminology (inappropriate for context, inconsistent use), or
(v) other errors.

Output only the new translation and nothing else. Please do not provide any explanations or text apart from the translation."""
    translation_2 = get_completion(prompt, system_message)
    return translation_2

def one_chunk_translate_text(source_lang: str, target_lang: str, source_text: str, country: str = "") -> str:
    translation_1 = one_chunk_initial_translation(source_lang, target_lang, source_text)
    reflection = one_chunk_reflect_on_translation(source_lang, target_lang, source_text, translation_1, country)
    translation_2 = one_chunk_improve_translation(source_lang, target_lang, source_text, translation_1, reflection)
    return translation_2

def main():
    st.title("Translation Assistant (Better than Google Translate!)")
    
    source_lang = st.selectbox("Source Language", ["English", "Chinese"])
    target_lang = st.selectbox("Target Language", ["Chinese", "English"])
    country = st.text_input("Country (Optional)")
    
    source_text = st.text_area("Input", "")

    if st.button("Do the Magic!"):
        with st.spinner("Translating..."):
            final_translation = one_chunk_translate_text(source_lang, target_lang, source_text, country)
            st.session_state['final_translation'] = final_translation
            st.text_area("Result", final_translation)


if __name__ == "__main__":
    main()
