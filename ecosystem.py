from dataclasses import dataclass
import json
from typing import Any
import itertools
import re
from functools import lru_cache


@dataclass
class Repo:
    url: str
    tags: Any = None


class Ecosystem:
    def __init__(self, path):
        with open(path) as f:
            self.projects = json.load(f)

    @property
    def all_projects(self):
        return self.projects.keys()

    def _flatten(self, iterable):
        return list(itertools.chain.from_iterable(iterable))

    def _make_exact_pat(self, s):
        return "^{}$".format(s)

    def _find_exact_matches(self, project, matches):
        exact_pat = self._make_exact_pat(project)
        return self._flatten(
            filter(
                None,
                [self._find_pat(m, exact_pat, flags=re.IGNORECASE) for m in matches],
            )
        )

    @lru_cache(maxsize=100)
    def get_repos(self, project: str):
        matches = self.find_project(project)
        exact_matches = self._find_exact_matches(project, matches)

        if len(matches) > 1 and len(exact_matches) > 1:
            print(
                "Multiple matches, please enter one of the following:\n\t{}".format(
                    "\n\t".join(matches)
                )
            )
            return None

        if len(exact_matches) > 0:
            entry = self.projects.get(exact_matches.pop())

            return {r.get("url").split("/")[-1]: Repo(**r) for r in entry.get("repo")}

        print("No matching projects")
        return None

    def _find_pat(self, s, pat, flags=None):
        return re.findall(pat, s, flags=flags) if flags else re.findall(pat, s)

    def find_project(self, project: str):
        pat = make_regex(project)
        matches = filter(
            None,
            map(
                lambda p: self._find_pat(p, pat, flags=re.IGNORECASE), self.all_projects
            ),
        )
        return list(itertools.chain.from_iterable(matches))


def make_regex(pat, sep=" "):
    parts = pat.split(sep)
    return ".*" + ".*".join(parts) + ".*"
