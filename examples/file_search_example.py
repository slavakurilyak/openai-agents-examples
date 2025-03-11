import asyncio
import os
from typing import List
from pydantic import BaseModel

from agents import Agent, FileSearchTool, Runner, function_tool, trace


class AgentPatternResult(BaseModel):
    """A structured result containing relevant agent patterns."""
    pattern_name: str
    description: str
    key_components: List[str]
    code_examples: List[str]
    recommended_use_cases: List[str]


@function_tool
def list_available_patterns() -> List[str]:
    """List all available agent patterns that can be searched for."""
    return [
        "Routing/Handoffs",
        "Agents as Tools",
        "Deterministic Flows",
        "LLM as a Judge",
        "Parallelization",
        "Input Guardrails",
        "Output Guardrails"
    ]


async def main():
    """Run an agent that helps developers find relevant agent patterns."""
    
    # In a real implementation, you would have already created a vector store
    # with your agent documentation and examples
    vector_store_id = "vs_your_agent_docs_store_id"
    
    agent = Agent(
        name="Agent Pattern Expert",
        instructions="""You are an expert on agent design patterns and implementation.
        Your goal is to help developers find the most relevant agent patterns for their use case.
        
        When asked about a specific pattern or use case:
        1. Search the documentation to find relevant agent patterns
        2. Explain the pattern's purpose, key components, and implementation details
        3. Provide code examples from the documentation
        4. Suggest use cases where this pattern would be most effective
        
        You can use the list_available_patterns tool to show all available patterns.
        """,
        tools=[
            FileSearchTool(
                vector_store_ids=[vector_store_id],
                max_num_results=5,
                include_search_results=True
            ),
            list_available_patterns
        ],
        output_type=AgentPatternResult,
    )

    with trace("Agent Pattern Search Workflow"):
        query = input("What agent pattern or use case are you looking for? ")
        result = await Runner.run(agent, query)
        
        # Print the structured output
        pattern = result.final_output
        print("\n===== AGENT PATTERN RECOMMENDATION =====\n")
        print(f"PATTERN: {pattern.pattern_name}")
        print(f"DESCRIPTION: {pattern.description}\n")
        
        print("KEY COMPONENTS:")
        for component in pattern.key_components:
            print(f"- {component}")
        print()
        
        print("CODE EXAMPLES:")
        for i, example in enumerate(pattern.code_examples, 1):
            print(f"\nExample {i}:")
            print(f"```python\n{example}\n```")
        print()
        
        print("RECOMMENDED USE CASES:")
        for use_case in pattern.recommended_use_cases:
            print(f"- {use_case}")


if __name__ == "__main__":
    # Note: This example requires setting up a vector store with agent documentation
    # You can create a vector store using the OpenAI API
    # See: https://platform.openai.com/docs/guides/tools-file-search
    asyncio.run(main())