# Import standard libraries
import argparse  # For handling command-line arguments
import os        # To access environment variables like the API key

# Import the FastMCP server framework
from mcp.server.fastmcp import FastMCP

# Import OpenAI client to use GPT models
import openai

# Load OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize the MCP server instance
# FastMCP allows you to expose functions as tools that can be called via MCP
mcp = FastMCP()

# Helper function to call the OpenAI Chat API with a given prompt
def call_llm(prompt: str, model="gpt-3.5-turbo", temperature=0.4) -> str:
    """Send a prompt to the OpenAI model and return its response text."""
    try:
        response = openai.ChatCompletion.create(
            model=model,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}],
        )
        # Return only the text content of the response
        return response.choices[0].message.content.strip()
    except Exception as e:
        # Catch and return any LLM-related errors
        return f"LLM error: {e}"

# -------------------------
# 🛠️ TOOL DEFINITIONS BELOW
# -------------------------

# Tool 1: Explain code
@mcp.tool()
def explain_code(code: str) -> str:
    """Explain what this code does in plain English."""
    prompt = f"Explain the following Python code in simple terms:\n\n{code}"
    return call_llm(prompt)

# Tool 2: Refactor code
@mcp.tool()
def refactor_code(code: str) -> str:
    """Refactor and clean up the code to improve clarity and performance."""
    prompt = f"Refactor and improve this Python code:\n\n{code}"
    return call_llm(prompt)

# Tool 3: Write unit tests
@mcp.tool()
def write_test(code: str) -> str:
    """Generate unit tests (Pytest-style) for the given code."""
    prompt = f"Write Pytest-style unit tests for this Python code:\n\n{code}"
    return call_llm(prompt)

# -------------------------
# 🚀 Start the MCP server
# -------------------------

if __name__ == "__main__":
    # Print a banner for clarity
    print("🚀 Developer Assistant MCP Server starting...")

    # Use argparse to allow passing --server_type (sse or stdio)
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--server_type", type=str, default="sse", choices=["sse", "stdio"]
    )

    # Parse command-line args
    args = parser.parse_args()

    # Start the MCP server using the chosen communication mode
    mcp.run(args.server_type)
