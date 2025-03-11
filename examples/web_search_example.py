import asyncio
from typing import List
from pydantic import BaseModel

from agents import Agent, Runner, WebSearchTool, trace


class AgentResearchReport(BaseModel):
    """A structured report about AI agent developments."""
    summary: str
    key_trends: List[str]
    notable_frameworks: List[str]
    challenges: List[str]
    future_directions: List[str]
    references: List[str]


async def main():
    """Run an agent that researches the latest developments in AI agents."""
    
    agent = Agent(
        name="Agent Researcher",
        instructions="""You are a specialized research agent focused on AI agents and autonomous systems.
        Your task is to research the latest developments, frameworks, and best practices in the field of AI agents.
        Focus particularly on:
        1. Recent advancements in multi-agent systems
        2. Tools and frameworks for building autonomous agents
        3. Challenges in agent development
        4. Future directions for agent technology
        
        Use web search to gather information, and produce a comprehensive research report.
        Be specific and detailed in your research, citing sources where appropriate.
        """,
        tools=[WebSearchTool(user_location={"type": "approximate", "city": "San Francisco"})],
        output_type=AgentResearchReport,
    )

    with trace("Agent Research Workflow"):
        query = input("What aspect of AI agents would you like to research? ")
        result = await Runner.run(agent, query)
        
        # Print the structured output
        report = result.final_output
        print("\n===== AGENT RESEARCH REPORT =====\n")
        print(f"SUMMARY:\n{report.summary}\n")
        
        print("KEY TRENDS:")
        for trend in report.key_trends:
            print(f"- {trend}")
        print()
        
        print("NOTABLE FRAMEWORKS:")
        for framework in report.notable_frameworks:
            print(f"- {framework}")
        print()
        
        print("CHALLENGES:")
        for challenge in report.challenges:
            print(f"- {challenge}")
        print()
        
        print("FUTURE DIRECTIONS:")
        for direction in report.future_directions:
            print(f"- {direction}")
        print()
        
        print("REFERENCES:")
        for ref in report.references:
            print(f"- {ref}")


if __name__ == "__main__":
    asyncio.run(main())