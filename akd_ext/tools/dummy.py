from akd._base import InputSchema, OutputSchema
from akd.tools import BaseTool
from pydantic import Field


class DummyInputSchema(InputSchema):
    """Input schema for the DummyTool."""

    query: str = Field(..., description="The query text to pass through")


class DummyOutputSchema(OutputSchema):
    """Output schema for the DummyTool."""

    query: str = Field(..., description="The query text returned unchanged")


class DummyTool(BaseTool[DummyInputSchema, DummyOutputSchema]):
    """
    Identity tool that returns the input query unchanged.
    Serves as a reference implementation for akd-ext tools.
    """

    input_schema = DummyInputSchema
    output_schema = DummyOutputSchema

    async def _arun(self, params: DummyInputSchema) -> DummyOutputSchema:
        """Return the input query as-is."""
        return DummyOutputSchema(query=params.query)
