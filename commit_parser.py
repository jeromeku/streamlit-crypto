import os
from functools import lru_cache

from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Any, List, Dict, Union, Optional
import pandas as pd
import toolz

from pydriller import Repository

COMMON_KEYS = [
    "hash",
    "author_date",
    "committer_date",
    "in_main_branch",
    "project_name",
    "project_path",
    "deletions",
    "insertions",
    "lines",
    "files",
]

DEFAULT_KEYS = COMMON_KEYS + ["author", "committer"]

DISPLAY_KEYS = [
    "author_date",
    "author_name",
    "author_email",
    "insertions",
    "deletions",
    "lines",
    "files",
]

STAT_KEYS = ["deletions", "insertions", "lines", "files"]

DATE_FORMAT = "%Y%m%d"


class CommitParser:
    DEFAULT_KEYS = [
        "hash",
        "author",
        "committer",
        "author_date",
        "committer_date",
        "in_main_branch",
        "project_name",
        "project_path",
        "deletions",
        "insertions",
        "lines",
        "files",
    ]

    DATE_FORMAT = "%Y%m%d"

    def __init__(self, download_dir="repos", *parse_keys):
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)
        self.download_dir = download_dir
        self.DEFAULT_KEYS.extend(parse_keys)

    def _format_author(self, row):
        row["author_name"] = row.get("author").name if row.get("author") else None
        row["author_email"] = row.get("author").email if row.get("author") else None
        row.pop("author")
        return row

    def _format_date(self, row):
        row["author_date"] = row["author_date"].strftime(self.DATE_FORMAT)
        row["committer_date"] = row["committer_date"].strftime(self.DATE_FORMAT)
        return row

    def _format_committer(self, row):
        row["committer_name"] = (
            row.get("committer").name if row.get("committer") else None
        )
        row["committer_email"] = (
            row.get("committer").email if row.get("committer") else None
        )
        row.pop("committer")
        return row

    def _format(self, commit):
        return toolz.compose(
            self._format_author, self._format_committer, self._format_date
        )(commit)

    def get_repo(self, repo):
        _repo = repo.split("/")[-1]
        local_path = os.path.join(self.download_dir, _repo)

        if not os.path.exists(local_path):
            print("Downloading repo")
            repo = Repository(repo, clone_repo_to=self.download_dir)
        else:
            print(f"Loading repo from {local_path}")
            repo = Repository(local_path)

        return repo

    def _process_commit(self, commit):
        return self._format({k: getattr(commit, k) for k in self.DEFAULT_KEYS})

    @lru_cache(maxsize=100)
    def get_summary(self, repo):
        repo = self.get_repo(repo)
        return [self._process_commit(commit) for commit in repo.traverse_commits()]

    # @lru_cache(maxsize=100)
    # def _get_summary_parallel(self, repo):
    #     repo = self.get_repo(repo)
    #     return Parallel(n_jobs=4)(
    #         delayed(self._process_commit)(commit) for commit in repo.traverse_commits()
    #     )


# def summarize_parallel(repo):
#     return Parallel(n_jobs=4)(
#         delayed(_process_commit)(commit) for commit in repo.traverse_commits()
#     )

# def _format_author(row):
#     row["author_name"] = row.get("author").name if row.get("author") else None
#     row["author_email"] = row.get("author").email if row.get("author") else None
#     row.pop("author")
#     return row


# def _format_date(row, date_fmt=DATE_FORMAT):
#     row["author_date"] = row["author_date"].strftime(date_fmt)
#     row["committer_date"] = row["committer_date"].strftime(date_fmt)
#     return row


# def _format_committer(row):
#     row["committer_name"] = row.get("committer").name if row.get("committer") else None
#     row["committer_email"] = (
#         row.get("committer").email if row.get("committer") else None
#     )
#     row.pop("committer")
#     return row


# def _format(commit):
#     return toolz.compose(_format_author, _format_committer, _format_date)(commit)


# def _process_commit(commit, keys=DEFAULT_KEYS):
#     return _format({k: getattr(commit, k) for k in keys})
