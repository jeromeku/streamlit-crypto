import shutil
from threading import local
from wsgiref import headers
import streamlit as st
import streamlit.components.v1 as components
import toml_parser
import json
import git
import os
import pandas as pd
import numpy as np
from commit_parser import CommitParser
import commit_parser
from ecosystem import Ecosystem

st.set_page_config(layout="wide")

LOCAL_PATH = os.environ.get("LOCAL_ECOSYSTEM_DIR", "data")
EXPORT_PATH = os.environ.get("EXPORT_PATH", "projects.json")
REPO_PATH = os.environ.get("REPO_PATH", "repos")

_fetch_repo_count_key = "FETCH_COUNT"
_parse_toml_count_key = "PARSE_COUNT"

if _fetch_repo_count_key not in st.session_state:
    st.session_state[_fetch_repo_count_key] = 0

if _parse_toml_count_key not in st.session_state:
    st.session_state[_parse_toml_count_key] = 0

ECOSYSTEM_REPO = "https://github.com/electric-capital/crypto-ecosystems.git"


@st.cache(suppress_st_warning=True)
def parse_toml(input_path, output_path):
    with st.spinner("Parsing ecosystems TOML..."):
        toml_parser.export(input_path, output_path)
    st.success(f"Done parsing!  Exported to {output_path}")
    st.session_state[_parse_toml_count_key] += 1


@st.cache(suppress_st_warning=True)
def fetch_repo(repo, path):
    if os.path.exists(LOCAL_PATH):
        shutil.rmtree(LOCAL_PATH)

    st.info(f"Cloning Electric Capital repo {ECOSYSTEM_REPO}")
    git.Repo.clone_from(ECOSYSTEM_REPO, LOCAL_PATH)
    st.session_state[_fetch_repo_count_key] += 1


def create_headers(columns):
    headers = "\n".join([f"<th>{col}</th>" for col in columns])
    return headers


def create_row(row):
    return "\n\t".join([f"<td>{col}</td>" for col in row])


def create_rows(rows):
    return "\n".join([create_row([row]) for row in rows])


def make_table(headers, rows):
    f"""
    <table>
    <tr>
        {headers}
    </tr>
    <tr>
       {rows}
    </tr>
    </table>"""


def create_table(entries, columns):
    headers = create_headers(columns)
    rows = create_rows(entries)
    # body = "\n\t".join([f"<tr>{row}</tr>" for row in rows])

    return make_table(headers, rows)


@st.cache(show_spinner=False)
def parse_repo(parser, repo):
    summary = parser.get_summary(repo.url)
    return (
        pd.DataFrame(summary)
        .assign(author_date=lambda df: pd.to_datetime(df.author_date))
        .assign(committer_date=lambda df: pd.to_datetime(df.committer_date))
    )


# for k in sorted(ecosystems.keys()):
#   st.write(f"\t{k}")

# st.info(f"Fetch repo count: {st.session_state[_fetch_repo_count_key]}")
# fetch_repo(ECOSYSTEM_REPO, LOCAL_PATH)
# st.info(f"Fetch repo count: {st.session_state[_fetch_repo_count_key]}")

# st.info(f"Parse count: {st.session_state[_parse_toml_count_key]}")
# parse_toml(os.path.join(LOCAL_PATH, "data"), EXPORT_PATH)
# st.info(f"Parse count: {st.session_state[_parse_toml_count_key]}")

with open(EXPORT_PATH) as f:
    ecosystems = json.load(f)

projects = sorted(ecosystems.keys())
project = st.selectbox("Please select project", options=projects)
ecosystem = Ecosystem(EXPORT_PATH)
repos = ecosystem.get_repos(project)
repo = st.selectbox(f"Repos for {project}", options=repos.keys())

# CSS to inject contained in a string
hide_table_row_index = """
            <style>
            tbody th {display:none}
            .blank {display:none}
            </style>
            """

# Inject CSS with Markdown
st.markdown(hide_table_row_index, unsafe_allow_html=True)
hide_dataframe_row_index = """
            <style>
            .row_heading.level0 {display:none}
            .blank {display:none}
            </style>
            """
st.markdown(hide_dataframe_row_index, unsafe_allow_html=True)

parser = CommitParser(REPO_PATH)
with st.spinner("Parsing repo"):
    df = parse_repo(parser, repos.get(repo))

st.dataframe(df[commit_parser.DISPLAY_KEYS], width=1000, height=500)


@st.cache
def get_stats(df, freq="1M", columns=commit_parser.STAT_KEYS):
    grouped = df.groupby(pd.Grouper(key="author_date", freq=freq))
    agg_funcs = {col: (col, "sum") for col in columns}
    agg_funcs.update(dict(commit_count=("author_name", "count")))
    return grouped.agg(**agg_funcs)


stats = get_stats(df)
st.dataframe(stats, width=1000, height=500)
import altair as alt

base = (
    alt.Chart(stats.reset_index())
    .mark_circle(opacity=0.0)
    .encode(
        alt.X("author_date:T", title="", axis=alt.Axis(grid=False)),
        alt.Y(
            "commit_count:Q",
            title="Commit Count",
        ),
    )
)

chart = (
    base
    + base.transform_loess("author_date", "commit_count", bandwidth=0.05).mark_area()
)

st.altair_chart(chart, use_container_width=True)
