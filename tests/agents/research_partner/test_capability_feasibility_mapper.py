"""Functional tests for CARE Capability & Feasibility Mapper Agent."""

import pytest

from akd._base import TextOutput
from akd_ext.agents.research_partner import (
    CapabilityFeasibilityMapperAgent,
    CapabilityFeasibilityMapperConfig,
    CapabilityFeasibilityMapperInputSchema,
    CapabilityFeasibilityMapperOutputSchema,
)


def _make_input(**overrides) -> CapabilityFeasibilityMapperInputSchema:
    """Helper to create input schema with default placeholder paths."""
    defaults = {
        "research_questions_path": "/path/to/research_questions.md",
        "slurm_template_path": "/path/to/slurm_template.sh",
        "cluster_it_pdf_path": "/path/to/cluster_it.pdf",
        "output_dir": "/path/to/output",
        "cm1_code_path": "/path/to/cm1/src",
        "cm1_readme_path": "/path/to/cm1/README.md",
        "cm1_notes_path": "/path/to/cm1/notes.md",
        "cm1_sample_case_path": "/path/to/cm1/sample_case",
        "cm1_namelist_dir": "/path/to/cm1/namelists",
        "cm1_namelist_filenames": ["namelist.input"],
        "cm1_run_script_path": "/path/to/cm1/run.sh",
        "cm1_logs_dir": "/path/to/cm1/logs",
    }
    defaults.update(overrides)
    return CapabilityFeasibilityMapperInputSchema(**defaults)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "research_questions_path",
    [
        "/path/to/tropical_cyclone_rqs.md",
        "/path/to/convective_initiation_rqs.md",
        "/path/to/boundary_layer_rqs.md",
    ],
)
async def test_capability_feasibility_mapper_agent(research_questions_path: str, reasoning_effort: str):
    """Test CARE Capability & Feasibility Mapper Agent.

    Args:
        research_questions_path: Path to research questions file
        reasoning_effort: CLI param --reasoning-effort (low/medium/high)
    """
    config = CapabilityFeasibilityMapperConfig(reasoning_effort=reasoning_effort)
    agent = CapabilityFeasibilityMapperAgent(config=config, debug=True)
    result = await agent.arun(_make_input(research_questions_path=research_questions_path))

    assert isinstance(result, (CapabilityFeasibilityMapperOutputSchema, TextOutput))
    if isinstance(result, CapabilityFeasibilityMapperOutputSchema):
        assert result.report.strip(), "Report should not be empty"
