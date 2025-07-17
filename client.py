
from llama_index.tools.mcp import BasicMCPClient, McpToolSpec
from llama_index.core.agent.workflow import FunctionAgent, ToolCallResult, ToolCall
from llama_index.core.workflow import Context
from llama_index.llms.ollama import Ollama
from llama_index.core import Settings

llm = Ollama(model="llama3.2", request_timeout=120.0)
Settings.llm = llm


# System prompt for the agent to be used with every tool call
SYSTEM_PROMPT = """\
You are an intelligent assistant that uses available tools to solve user problems.
When helpful, call tools to complete tasks before responding.
"""
#takes in mcptoolspec (list of tools defined in client) and returns an agent that can use these tools
async def get_agent(tools: McpToolSpec) -> FunctionAgent:
    """Create and return a FunctionAgent with the given tools."""
    tools = await tools.to_tool_list_async()
    agent = FunctionAgent(
        name="Agent",
        description="An agent that can work with any MCP-compatible tools.",
        tools=tools,
        llm=llm,
        system_prompt=SYSTEM_PROMPT,
    )
    return agent

async def handle_user_message(message_content: str, agent: FunctionAgent, agent_context: Context, verbose: bool = False) -> str:
    """Handle a user message using the agent."""
    #starts the agent with message and context, returns handler, which manages the ongoing async task
    handler = agent.run(message_content, ctx=agent_context)
    #get events from handler stream in real time asynchronously (toolcalls and results).
    async for event in handler.stream_events():
        #if verbose enabled, print tool calls and tool call results
        if verbose and type(event) == ToolCall:
            print(f"Calling tool {event.tool_name} with kwargs {event.tool_kwargs}")
        elif verbose and type(event) == ToolCallResult:
            print(f"Tool {event.tool_name} returned {event.tool_output}")

    #wait for handler of agent to finish and return the final response
    response = await handler
    return str(response)

async def main():
    # initialize MCP client and tool spec. communicates with server over SSE 
    # (continuous one-way stream from server to client to stream events)
    mcp_client = BasicMCPClient("http://127.0.0.1:8000/sse")
    # get the tools defined in client
    mcp_tool = McpToolSpec(client=mcp_client)
    
    # get the agent
    agent = await get_agent(mcp_tool)
    
    # create the agent context, agent will log tool calls and results in this context
    agent_context = Context(agent)
    
    # get tool description list and print the available tools
    tools = await mcp_tool.to_tool_list_async()
    print("Available tools:")
    for tool in tools:
        print(f"{tool.metadata.name}: {tool.metadata.description}")
    
    # main interaction loop
    print("\nEnter 'exit' to quit")
    while True:
        try:
            user_input = input("\nEnter your message: ")
            if user_input.lower() == "exit":
                break
                
            print(f"\nUser: {user_input}")
            response = await handle_user_message(user_input, agent, agent_context, verbose=True)
            print(f"Agent: {response}")
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 