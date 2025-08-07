# This would be in your main testing script, e.g., scripts/run_aiz.py

import os
from dotenv import load_dotenv

load_dotenv()

aws_bedrock_config = {
    "provider": "aws_bedrock", 
    "aws_access_key_id": os.getenv("AWS_ACCESS_KEY_ID"),
    "aws_secret_access_key": os.getenv("AWS_SECRET_ACCESS_KEY"),
    "aws_session_token": os.getenv("AWS_SESSION_TOKEN"),
    "model_id": "anthropic.claude-3-sonnet-20240229-v1:0", # A great, balanced choice
    "region_name": "us-east-1", # Or whichever region you use for Bedrock
    "temperature": 0.1,
    "max_tokens": 2048,
}

from aiz.builders.provider_bulders import ProviderFactory

factory = ProviderFactory()

try:
    llm = factory.build(aws_bedrock_config)
    print("Successfully built Bedrock LLM instance:")
    print(llm)

    # You could even test it
    from langchain_core.messages import HumanMessage
    response = llm.invoke([HumanMessage(content="Hello, world!")])
    print("\nLLM Response:")
    print(response.content)

except Exception as e:
    print(f"An error occurred: {e}")
