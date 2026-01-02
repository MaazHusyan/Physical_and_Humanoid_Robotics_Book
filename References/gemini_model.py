import os
from agents import (
    AsyncOpenAI,
    OpenAIChatCompletionsModel,
    RunConfig
)
from dotenv import load_dotenv, find_dotenv


# Load environment variables from .env file
_: bool = load_dotenv(find_dotenv())

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "") #ONLY FOR ENABLING TRACING


# Try Gemini API first
gemini_api_key = os.getenv("GEMINI_API_KEY")
gemini_base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"

# Check if we can initialize the model - first try Gemini
client = None
geminiModel = None
MODEL_AVAILABLE = False
config = None

if gemini_api_key:
    try:
        # Try to use Gemini API
        client = AsyncOpenAI(
            api_key = gemini_api_key,
            base_url = gemini_base_url,
        )

        geminiModel = OpenAIChatCompletionsModel(
            openai_client = client,
            model="gemini-2.5-flash", # Using gemini-2.5-flash model
        )

        # Test the client with a simple operation to check if quota is exceeded
        MODEL_AVAILABLE = True
    except Exception as e:
        print(f"Gemini API unavailable (possibly quota exceeded): {e}")
        # Gemini failed, try OpenAI as fallback
        client = None
        geminiModel = None

# If Gemini is not available or failed, try OpenAI
if not MODEL_AVAILABLE:
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if openai_api_key:
        try:
            openai_base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
            client = AsyncOpenAI(
                api_key = openai_api_key,
                base_url = openai_base_url,
            )

            geminiModel = OpenAIChatCompletionsModel(
                openai_client = client,
                model="gpt-3.5-turbo", # Using gpt-3.5-turbo as a fallback
            )

            MODEL_AVAILABLE = True
        except Exception as e:
            print(f"OpenAI API also unavailable: {e}")
            client = None
            geminiModel = None
            MODEL_AVAILABLE = False

# configuring the model/config - only if models are available
if MODEL_AVAILABLE and geminiModel is not None:
    config = RunConfig(
        model = geminiModel,
        model_provider = client,
        tracing_disabled=True
    )
else:
    config = None
    geminiModel = None
    client = None
    MODEL_AVAILABLE = False