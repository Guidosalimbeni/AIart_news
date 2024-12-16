from app.core.config import get_settings
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel

def test_environment():
    print("Testing environment setup...")
    
    # Test settings
    settings = get_settings()
    print("\n1. Testing configuration:")
    print(f"Output directory: {settings.OUTPUT_DIR}")
    
    # Test Pydantic AI
    print("\n2. Testing Pydantic AI setup:")
    
    # Initialize OpenAI model with API key from settings
    model = OpenAIModel('gpt-3.5-turbo', api_key=settings.OPENAI_API_KEY)
    agent = Agent(model)
    
    try:
        result = agent.run_sync('Say "Hello, World!"')
        print(f"Agent response: {result.data}")
        print("\nEnvironment setup successful! ")
    except Exception as e:
        print(f"Error testing agent: {str(e)}")
        print("\nPlease check your API keys and try again.")

if __name__ == "__main__":
    test_environment()
