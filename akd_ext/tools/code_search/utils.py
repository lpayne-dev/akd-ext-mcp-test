from github import Github, Auth
from pydantic import BaseModel, Field

class RepositoryMetadata(BaseModel):
  """
    Github repository metadata. includes number of stars, forks, open issues, open pull requests, and closed pull requests.
  """
  stars: int = Field(default=0, description="Number of stars on the repository.")
  forks: int = Field(default=0, description="Number of forks on the repository.")
  open_issues: int = Field(default=0, description="Number of open issues on the repository.")
  pulls: int = Field(default=0, description="Number of open pull requests on the repository.")
  closed_pulls: int = Field(default=0, description="Number of closed pull requests on the repository.")

async def fetch_github_metadata(repo_name: str, access_token: str | None = None) -> RepositoryMetadata:
  """
    Repo_name should be in the format of owner/repo
  """
  auth = None
  repository_metadata: RepositoryMetadata = RepositoryMetadata()
  if access_token:
    auth = Auth.Token(access_token)
  with Github(auth=auth) as g:
    repo = g.get_repo(repo_name)
    repository_metadata.stars = repo.stargazers_count
    repository_metadata.forks = repo.forks_count
    repository_metadata.open_issues = repo.get_issues(state='open').totalCount
    repository_metadata.pulls = repo.get_pulls(state='open', sort='created', base='master').totalCount
    repository_metadata.closed_pulls = repo.get_pulls(state='closed', sort='created', base='master').totalCount
  return repository_metadata


def get_reliability_score(repository_metadata: RepositoryMetadata) -> float:
  # TODO: use reliability score calculation formula
  return 1.0
