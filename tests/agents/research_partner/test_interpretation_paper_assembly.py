"""Functional tests for Interpretation & Paper Assembly Agent."""

import pytest

from akd._base import TextOutput
from akd_ext.agents.research_partner import (
    InterpretationPaperAssemblyAgent,
    InterpretationPaperAssemblyConfig,
    InterpretationPaperAssemblyInputSchema,
    InterpretationPaperAssemblyOutputSchema,
)


def _make_input(**overrides) -> InterpretationPaperAssemblyInputSchema:
    """Helper to create input schema with default placeholder values."""
    defaults = {
        "research_question_path": "/path/to/research_question.md",
        "ctl_path": "/path/to/experiment/cm1out.ctl",
        "analysis_dir": "/path/to/analysis",
    }
    defaults.update(overrides)
    return InterpretationPaperAssemblyInputSchema(**defaults)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "research_question_path,ctl_path",
    [
        (
            "/path/to/tropical_cyclone_rq.md",
            "/path/to/tc_experiment/cm1out.ctl",
        ),
        (
            "/path/to/boundary_layer_rq.md",
            "/path/to/bl_experiment/cm1out.ctl",
        ),
        (
            "/path/to/convective_initiation_rq.md",
            "/path/to/ci_experiment/cm1out.ctl",
        ),
    ],
)
async def test_interpretation_paper_assembly_agent(research_question_path: str, ctl_path: str, reasoning_effort: str):
    """Test Interpretation & Paper Assembly Agent.

    Args:
        research_question_path: Path to research question file
        ctl_path: Path to GrADS control file
        reasoning_effort: CLI param --reasoning-effort (low/medium/high)
    """
    config = InterpretationPaperAssemblyConfig(reasoning_effort=reasoning_effort)
    agent = InterpretationPaperAssemblyAgent(config=config, debug=True)
    result = await agent.arun(_make_input(research_question_path=research_question_path, ctl_path=ctl_path))

    assert isinstance(result, (InterpretationPaperAssemblyOutputSchema, TextOutput))
    if isinstance(result, InterpretationPaperAssemblyOutputSchema):
        assert result.report.strip(), "Report should not be empty"


@pytest.mark.asyncio
async def test_interpretation_paper_assembly_with_figures(reasoning_effort: str):
    """Test that providing figures_dir triggers report generation.

    Args:
        reasoning_effort: CLI param --reasoning-effort (low/medium/high)
    """
    config = InterpretationPaperAssemblyConfig(reasoning_effort=reasoning_effort)
    agent = InterpretationPaperAssemblyAgent(config=config, debug=True)
    result = await agent.arun(_make_input(figures_dir="/path/to/figures_experiment01"))

    assert isinstance(result, (InterpretationPaperAssemblyOutputSchema, TextOutput))
    if isinstance(result, InterpretationPaperAssemblyOutputSchema):
        assert result.report.strip(), "Report should not be empty"
