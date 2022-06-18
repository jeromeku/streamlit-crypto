import streamlit as st
import toml_parser
import git
import os

local_path = os.environ.get("LOCAL_ECOSYSTEM_DIR", "data")
export_path = os.environ.get("EXPORT_PATH", "projects.json")

ECOSYSTEM_REPO = "https://github.com/electric-capital/crypto-ecosystems"

st.info(f"Stored secrets: {dir(st.secrets)}")
st.info(f"Cloning Electric Capital repo {ECOSYSTEM_REPO}")
git.Repo.clone_from(ECOSYSTEM_REPO, local_path)

with st.spinner("Parsing ecosystems TOML..."):
    toml_parser.export(os.path.join(local_path, "data"), export_path)
st.success(f"Done parsing!  Exported to {export_path}")
