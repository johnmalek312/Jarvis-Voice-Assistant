"""This module contains the GPTResearcher class, which is used to conduct researches over the web."""
from typing import Annotated

from config import researcher_config
researcher_config() # Load the researcher config
from tool_registry import register_tool
from gpt_researcher import GPTResearcher


@register_tool()
async def conduct_research(query: Annotated[str, "The query to conduct research on"]) -> str:
    """
    This function conducts research on the given query and returns the report.

    This uses the GPTResearcher which conduct deep research on the given query.

    This takes some time to complete.
    """
    # Report Type
    report_type = "research_report"

    # Initialize the researcher
    researcher = GPTResearcher(query=query, report_type=report_type, config_path=None)
    # Conduct research on the given query
    await researcher.conduct_research()
    # Write the report
    report = await researcher.write_report()

    return "Research finished, summarize the report concisely into 100-300words unless specified otherwise or seemed irrational. \n\nHere is the report ```" + report + "```"
