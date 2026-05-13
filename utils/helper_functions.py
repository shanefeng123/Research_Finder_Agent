from agents import (
    AgentUpdatedStreamEvent,
    ItemHelpers,
    MessageOutputItem,
    RawResponsesStreamEvent,
    RunItemStreamEvent,
    Runner,
)
from openai.types.responses.response_text_delta_event import ResponseTextDeltaEvent


def agent_label(agent):
    return agent.name


def store_messages(result, conversation):
    stored_any = False
    for item in result.new_items:
        if not isinstance(item, MessageOutputItem):
            continue

        text = ItemHelpers.text_message_output(item)
        if not text:
            continue

        conversation.append(
            {
                "role": "assistant",
                "content": text,
            }
        )
        stored_any = True

    if not stored_any:
        conversation.append(
            {
                "role": "assistant",
                "content": result.final_output,
            }
        )


async def run_streamed_and_store(starting_agent, input_data, conversation, research_state):
    result = Runner.run_streamed(starting_agent, input_data, context=research_state)
    current_agent = starting_agent
    printed_label = False

    async for event in result.stream_events():
        if isinstance(event, AgentUpdatedStreamEvent):
            if printed_label:
                print()
            current_agent = event.new_agent
            printed_label = False
            continue

        if isinstance(event, RawResponsesStreamEvent):
            if isinstance(event.data, ResponseTextDeltaEvent):
                if not printed_label:
                    print(f"\n{agent_label(current_agent)}: ", end="", flush=True)
                    printed_label = True
                print(event.data.delta, end="", flush=True)
            continue

        if isinstance(event, RunItemStreamEvent):
            if event.name == "handoff_requested" and printed_label:
                print()
                printed_label = False

    if printed_label:
        print()

    store_messages(result, conversation)
    return result
