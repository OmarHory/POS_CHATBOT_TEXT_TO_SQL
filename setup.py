from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="lex_sitech_bot",
    version="0.1",
    packages=find_packages(),
    install_requires=requirements,
    entry_points={},
    author="Omar Alhory",
    author_email="omar@sitech.me",
    description="A package for the lex sitech bot, it utilizes GPT with Database Chaining to answer SQL queries.",
    url="https://github.com/OmarHory/gpt_whatsapp",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
