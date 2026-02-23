import asyncio
import os
from urllib.parse import urlparse

from loguru import logger
from pydantic import AnyUrl, BaseModel, Field
from akd.tools import BaseTool
from akd.tools.search.code_search import (
    CodeSearchToolInputSchema,
    CodeSearchToolOutputSchema,
    SDECodeSearchTool,
    SDECodeSearchToolConfig,
)
from akd.structures import SearchResultItem

from akd_ext.mcp import mcp_tool
from .utils import RepositoryMetadata, fetch_github_metadata, calculate_reliability_score


class RepositorySearchResultItem(BaseModel):
    """
    Repository search result item.
    """

    url: AnyUrl = Field(..., description="Repository URL.")
    full_text: str = Field(..., description="SDE-indexed repository README/content text.")
    reliability_score: float | None = Field(
        default=None,
        description="Computed reliability score based on github repository metadata. If none, treat it neutrally as if there is no reliability score.",
    )
    repository_metadata: RepositoryMetadata = Field(
        default_factory=RepositoryMetadata,
        description="Github repository metadata. includes number of stars, forks, open issues, open pull requests, and closed pull requests.",
    )


# Tool input and output schemas
class RepositorySearchToolInputSchema(CodeSearchToolInputSchema):
    """
    Input query for the repository search tool. Its a text based query that initializes the relevant code search tool.
    """


class RepositorySearchToolOutputSchema(BaseModel):
    """
    Output schema for the repository search tool.
    """

    results: list[RepositorySearchResultItem] = Field(
        ...,
        description="List of repository search items.",
    )


# Tool config schema
class RepositorySearchToolConfig(SDECodeSearchToolConfig):
    """
    Config schema for the repository search tool.
    """

    access_token: str | None = Field(default=os.getenv("GITHUB_ACCESS_TOKEN", None), description="GitHub access token")


# Tool implementation
@mcp_tool
class RepositorySearchTool(BaseTool[RepositorySearchToolInputSchema, RepositorySearchToolOutputSchema]):
    """
    Search for relevant code and implementations within specialized science repositories.

    This tool performs a targeted search across curated scientific codebases to find
    relevant GitHub repositories with README. It enriches the search results with
    GitHub metadata such as stars, forks, and development activity, which are then
    used to compute a reliability score for each item.

    The reliability score (0-100) is a weighted average of repository maturity, activity, and community trust.

    The formula: Score = (Age * 0.20) + (Activity * 0.25) + (Stars * 0.25) + (Forks * 0.15) + (History * 0.15)

    How components are calculated:
      - Age (20%): Higher for older repos; reaches 100% after 4 years.
      - Activity (25%): Starts at 100% and drops to 0% if the repo hasn't been updated in a year.
      - Stars (25%): Logarithmic scale where ~1,000 stars = 100%.
      - Forks (15%): Logarithmic scale where ~500 forks = 100%.
      - History (15%): Based on the span between the first commit and now; reaches 100% after 4 years.
    """

    input_schema = RepositorySearchToolInputSchema
    output_schema = RepositorySearchToolOutputSchema
    config_schema = RepositorySearchToolConfig

    async def _arun(self, params: RepositorySearchToolInputSchema) -> RepositorySearchToolOutputSchema:
        sde_tool = SDECodeSearchTool(config=self._build_sde_config())
        search_result: CodeSearchToolOutputSchema = await sde_tool.arun(params)
        tasks: list[asyncio.Task] = [
            self._enrich_code_search_with_metadata(repository_item) for repository_item in search_result.results
        ]
        enriched_results: list[RepositorySearchResultItem] = await asyncio.gather(*tasks)
        repository_search_result: RepositorySearchToolOutputSchema = RepositorySearchToolOutputSchema(
            results=enriched_results
        )
        return repository_search_result

    async def _enrich_code_search_with_metadata(self, repository_item: SearchResultItem) -> RepositorySearchResultItem:
        repository_metadata: RepositoryMetadata = RepositoryMetadata()
        reliability_score: float | None = None
        repo_name = self._extract_repo_name(str(repository_item.url))
        if repo_name:
            repository_metadata = await fetch_github_metadata(repo_name, self.config.access_token)
            reliability_score = calculate_reliability_score(repository_metadata)

        return RepositorySearchResultItem(
            url=repository_item.url,
            full_text=repository_item.content or "",
            repository_metadata=repository_metadata,
            reliability_score=reliability_score,
        )

    def _build_sde_config(self) -> SDECodeSearchToolConfig:
        return SDECodeSearchToolConfig(
            base_url=self.config.base_url,
            page_size=self.config.page_size,
            max_pages=self.config.max_pages,
            headers=self.config.headers,
            debug=self.config.debug,
            search_mode=self.config.search_mode,
        )

    def _extract_repo_name(self, url: str) -> str | None:
        if not url:
            return None
        parsed_url = urlparse(url)
        host = parsed_url.netloc.lower()
        if host not in {"github.com", "www.github.com"}:
            return None
        path_parts = [part for part in parsed_url.path.strip("/").split("/") if part]
        if len(path_parts) < 2:
            return None
        owner = path_parts[0]
        repo = path_parts[1].removesuffix(".git")
        if not owner or not repo:
            return None
        return f"{owner}/{repo}"


if __name__ == "__main__":
    import asyncio
    import sys

    config = RepositorySearchToolConfig(page_size=2)
    query = "indus pipeline code"
    if len(sys.argv) > 1:
        query = sys.argv[1]
    tool = RepositorySearchTool(config=config)
    result = asyncio.run(tool.arun(RepositorySearchToolInputSchema(queries=[query])))
    logger.info(result.model_dump())
