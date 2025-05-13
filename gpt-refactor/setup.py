from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="gpt-refactor",
    version="1.0.0",
    author="raayanTamuly",
    author_email="author@example.com",
    description="AI-powered code refactoring tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SirCodeKnight/gpt-refactor",
    project_urls={
        "Bug Tracker": "https://github.com/SirCodeKnight/gpt-refactor/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.7",
    install_requires=[
        "openai>=0.27.0",
        "flask>=2.0.0",
        "flask-cors>=3.0.10",
        "click>=8.0.0",
        "colorama>=0.4.4",
        "requests>=2.25.0",
        "werkzeug>=2.0.0",
    ],
    entry_points={
        "console_scripts": [
            "gpt-refactor=src.cli.cli:main",
        ],
    },
)