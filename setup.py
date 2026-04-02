from setuptools import setup, find_packages

setup(
    name="roadmap-ai",
    version="0.1.0",
    description="Never lose the thread again - Continuity engine for projects",
    packages=find_packages(),
    install_requires=[
        "click>=8.1.0",
        "sqlalchemy>=2.0.0",
        "openai>=1.0.0",
        "python-dotenv>=1.0.0",
        "jsonschema>=4.0.0",
    ],
    entry_points={
        "console_scripts": [
            "roadmap=roadmap.cli:main",
        ],
    },
    python_requires=">=3.11",
)
