from google.adk.agents.llm_agent import Agent
from .gmail_tools import list_messages, get_message_content, search_messages, export_to_csv

root_agent = Agent(
    model='gemini-2.5-flash',
    name='gmail_extractor',
    description='A Gmail extraction assistant that can list, search, retrieve, and export email messages to CSV.',
    instruction="""You are a Gmail extraction assistant. You can help users:
    - List recent emails
    - Search for specific emails using Gmail query syntax
    - Retrieve full content of specific messages
    - Export email results to CSV format

    Use the available tools to access Gmail data and provide helpful information to users.""",
    tools=[list_messages, get_message_content, search_messages, export_to_csv],
)
