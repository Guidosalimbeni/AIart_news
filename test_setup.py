from app.core.config import get_settings
from pydantic_ai import Agent
import asyncio

async def test_environment():
    print("Testing environment setup...")
    
    # Test settings
    settings = get_settings()
    print("\n1. Testing configuration:")
    print(f"Output directory: {settings.OUTPUT_DIR}")
    
    # Test Pydantic AI
    print("\n2. Testing Pydantic AI setup:")
    agent = Agent(
        'anthropic:claude-3-opus-20240229',
        system_prompt='You are a helpful assistant.'
    )
    
    try:
        result = await agent.arun('Say "Hello, World!"')
        print(f"Agent response: {result.data}")
        print("\nEnvironment setup successful! ✅")
    except Exception as e:
        print(f"Error testing agent: {str(e)}")
        print("\nPlease check your API keys and try again.")

if __name__ == "__main__":
    asyncio.run(test_environment())
