import streamlit as st
import toml_parser
import git
import os

LOCAL_ECOSYSTEM_DIR = "ecosystems"
EXPORT_PATH = "ecosystems.json"
ECOSYSTEM_REPO = "https://github.com/electric-capital/crypto-ecosystems"

st.info(f"Cloning Electric Capital repo {ECOSYSTEM_REPO}")
git.Repo.clone_from(ECOSYSTEM_REPO, LOCAL_ECOSYSTEM_DIR)

with st.spinner("Parsing ecosystems TOML..."):
    toml_parser.export(os.path.join(LOCAL_ECOSYSTEM_DIR, "data"), EXPORT_PATH)
st.success(f"Done parsing!  Exported to {EXPORT_PATH}")
