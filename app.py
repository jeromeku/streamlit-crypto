import streamlit as st
import toml_parser
import json
import git
import os

local_path = os.environ.get("LOCAL_ECOSYSTEM_DIR", "data")
export_path = os.environ.get("EXPORT_PATH", "projects.json")
_fetch_repo_count_key = 'FETCH_COUNT'
_parse_toml_count_key = 'PARSE_COUNT'

if _fetch_repo_count_key not in st.session_state:
    st.session_state[_fetch_repo_count_key] = 0

if _parse_toml_count_key not in st.session_state:
    st.session_state[_parse_toml_count_key] = 0

ECOSYSTEM_REPO = "https://github.com/electric-capital/crypto-ecosystems"

@st.cache
def parse_toml(input_path, output_path):
    st.write(f"Parse count: {st.session_state[_parse_toml_count_key]}")
    with st.spinner("Parsing ecosystems TOML..."):
        toml_parser.export(input_path, output_path)
    st.success(f"Done parsing!  Exported to {output_path}")
    st.session_state[_parse_toml_count_key] += 1
    st.write(f"Parse count: {st.session_state[_parse_toml_count_key]}")

@st.cache
def fetch_repo(repo, path):
    st.write(f"Fetch repo count: {st.session_state[_fetch_repo_count_key]}")
    st.info(f"Cloning Electric Capital repo {ECOSYSTEM_REPO}")
    git.Repo.clone_from(ECOSYSTEM_REPO, local_path)
    st.session_state[_fetch_repo_count_key] += 1
    st.write(f"Fetch repo count: {st.session_state[_fetch_repo_count_key]}")
    
fetch_repo(ECOSYSTEM_REPO, local_path)
parse_toml(os.path.join(local_path, "data"), export_path)

with open(export_path) as f:
    ecosystems = json.load(f)

st.header("Parsed Ecosystems:")
for k in ecosystems.keys():
    st.write(f"\t{k}")