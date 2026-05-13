import asyncio

from agents import (
    Agent,
    trace,
)
from dotenv import load_dotenv

from utils.helper_functions import run_streamed_and_store
from utils.prompts import *
from utils.tools import *

load_dotenv(override=True)

email_agent = Agent(
    name="EmailAgent",
    instructions=email_agent_prompt,
    model="gpt-4o-mini",
    tools=[get_research_request, send_email],
    handoff_description="Send the final list of papers to the user's email address specified in the research request",
)

paper_filtering_agent = Agent(
    name="PaperFilteringAgent",
    instructions=LLM_filtering_prompt,
    model="gpt-4o-mini",
    tools=[get_research_request, filter_papers],
    handoffs=[email_agent],
    handoff_description="Filter the retrieved papers based on the research interest specified by the user and the similarity method specified by the user",
)

paper_searching_agent = Agent(
    name="PaperSearchingAgent",
    instructions=paper_searching_prompt,
    model="gpt-4o-mini",
    tools=[get_research_request, search_arxiv],
    handoffs=[paper_filtering_agent],
    handoff_description="Search research papers based on the topics and the number of papers specified",
)

reception_agent = Agent(
    name="ReceptionAgent",
    instructions=reception_agent_prompt,
    model="gpt-4o-mini",
    tools=[record_research_request],
    handoffs=[
        paper_searching_agent,
    ],
)


async def main():
    conversation = []
    research_state = ResearchState()
    # Let the agent generate its own opening message
    await run_streamed_and_store(
        reception_agent,
        "Start the conversation with the user.",
        conversation,
        research_state,
    )

    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in {"exit", "quit", "q"}:
            print("ReceptionAgent: Goodbye!")
            break

        conversation.append(
            {
                "role": "user",
                "content": user_input,
            }
        )

        with trace("Research Finder Agent"):
            await run_streamed_and_store(
                reception_agent,
                conversation,
                conversation,
                research_state,
            )


if __name__ == "__main__":
    asyncio.run(main())
