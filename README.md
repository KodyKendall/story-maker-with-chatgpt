This is a project that uses LLMs to generate stories and essays.

Large Language Models are really fun tools for learning about the world and exploring ideas.

Audio and Images help bring the stories & ideas to life, which helps us learn and remember them better.

This project is a collection of tools that I've built to help me create audio and images to accompany the text generated by the LLMs.

Here's how it works:

1. create a .txt file that has the text content you want to convert into audio & accompanying images.
2. A large language model takes the .txt, and turns it into descriptions of images that accompany the text.

### Set Up Instructions:

# Set up your virtual environment
`python -m venv venv`
`source venv/bin/activate`
`pip install -r requirements.txt`

# Set up your OpenAI and LangSmith API keys:

```
touch .env
```

```
nano .env
```

Copy and paste the following into the .env file:
```
OPENAI_API_KEY=sk-0000000000000000000000000000000000000000000000000000000000000000
LANGSMITH_API_KEY=lsv2_0000000000000000000000000000000000000000000000000000000000000000
```

Replace the API Keys with your own. To get your API keys, go to the following websites:
- OpenAI: https://platform.openai.com/
- LangSmith: https://smith.langchain.com/

# Run the project
`python app.py`

# Run the project with Uvicorn
`uvicorn app:app --reload`

Go to http://127.0.0.1:8000/ to see the project running.