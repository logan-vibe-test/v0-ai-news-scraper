from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ai-voice-scraper",
    version="1.0.0",
    author="AI Voice News Team",
    author_email="your-email@example.com",
    description="Monitor AI voice technology news and community discussions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/ai-voice-news-scraper",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "aiohttp>=3.8.0",
        "beautifulsoup4>=4.11.0",
        "python-dotenv>=1.0.0",
        "feedparser>=6.0.0",
        "langchain>=0.1.0",
        "langchain-community>=0.0.10",
        "langchain-openai>=0.0.2",
        "openai>=1.6.1",
        "motor>=3.3.0",
        "pymongo>=4.6.0",
        "praw>=7.7.0",
        "prawcore>=2.3.0",
        "requests>=2.28.0",
        "urllib3>=1.26.0",
        "certifi>=2023.0.0",
        "slack-sdk>=3.26.0",
        "jinja2>=3.1.0",
    ],
    entry_points={
        "console_scripts": [
            "ai-voice-scraper=ai_voice_scraper.cli:main",
        ],
    },
)
