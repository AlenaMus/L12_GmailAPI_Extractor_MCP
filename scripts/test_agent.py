"""Test script to interact with the Gmail extractor agent."""
from gmail_extractor.agent import root_agent
from google.adk.runners import InMemoryRunner
from google.genai import types
import uuid

# Test the agent
if __name__ == "__main__":
    print("Testing Gmail Extractor Agent...")
    print("=" * 80)

    # Test query
    query = "List my last 5 emails"
    print(f"\nQuery: {query}\n")

    # Create runner
    runner = InMemoryRunner(agent=root_agent)

    # Generate unique IDs
    user_id = "test_user"
    session_id = str(uuid.uuid4())

    # Create message content
    content = types.Content(role='user', parts=[types.Part(text=query)])

    # Create session first
    runner.create_session(user_id=user_id, session_id=session_id)

    # Run the agent
    events = runner.run(
        user_id=user_id,
        session_id=session_id,
        new_message=content
    )

    # Print the response
    print("Response:")
    print("=" * 80)
    for event in events:
        if hasattr(event, 'content'):
            print(event.content)
        else:
            print(event)
