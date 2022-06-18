import streamlit as st
import toml_parser
import git
import os

git.Repo.clone_from("https://github.com/electric-capital/crypto-ecosystems", "crypto-ecosystems")


st.write("### Hello World!")
st.write(f'{os.listdir(".")}')