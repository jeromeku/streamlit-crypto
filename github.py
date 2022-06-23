import os
import httpx

class GitHubClient():
    BASE_URL: str = "https://api.github.com"
    
    def __init__(self, api_key=None):
        self._api_key = api_key
        self.client = httpx.Client(base_url=self.BASE_URL)
        self._headers = { "Accept": "application/vnd.github.v3+json" }

    def get(self, url, headers=None, **params):
        headers = { **self._headers, **headers } if headers else self._headers
        return self.client.get(url, headers=headers, params=params)

class GithubStats(GitHubClient):
    _end_point: str = "/repos/{owner}/{repo}/{endpoint}"
    
    def _make_endpoint(self, owner, repo, endpoint):
        return self._end_point.format(owner=owner, repo=repo, endpoint=endpoint)
    
    def get_contributors(self, owner, repo):
        end_point = self._make_endpoint(owner, repo, 'stats/contributors')
        print(end_point)
        return self.get(end_point)

    def get_commit_activity(self, owner, repo):
        end_point = self._make_endpoint(owner, repo, 'stats/commit_activity')
        print(end_point)
        return self.get(end_point)

    def get_code_frequency(self, owner, repo):
        end_point = self._make_endpoint(owner, repo, 'stats/code_frequency')
        return self.get(end_point)

    def get_commits(self, owner, repo, per_page=100, page=1):
        end_point = self._make_endpoint(owner, repo, 'commits')
        return self.get(end_point, per_page=per_page, page=page)

    def get_commit(self, owner, repo, ref, per_page=100, page=1):
        end_point = os.path.join(self._make_endpoint(owner, repo, f'commits/{ref}'))
        return self.get(end_point, per_page=per_page, page=page)
    
    def get_events(self, owner, repo, per_page=100, page=1):
        end_point = self._make_endpoint(owner, repo, 'events')
        return self.get(end_point, per_page=per_page, page=page)

    def get_stars(self, owner, repo, per_page=100, page=1):
        end_point = self._make_endpoint(owner, repo, 'stargazers')
        return self.get(end_point, headers={'Accept': 'application/vnd.github.v3.star+json'}, per_page=per_page, page=page)
 
        