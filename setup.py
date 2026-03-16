from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="t2s-metrics",
    version="1.0.2",
    packages=find_packages(),
    install_requires=[
        "nltk==3.9.2",
        "rouge_score==0.1.2",
        "scikit-learn==1.8.0",
        "Levenshtein==0.27.3",
        "rdflib==7.5.0",
        "langchain_ollama==1.0.1",
        "SPARQLWrapper==2.0.0",
        "dash==4.0.0",
        "dash_bootstrap_components==2.0.4",
        "pandas==3.0.1",
    ],
    extras_require={
        "dev": [
            "pytest==9.0.2",
            "twine==6.2.0",
        ],
        "build": [
            "setuptools==80.9.0",
            "wheel==0.45.1",
        ],
    },
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Wimmics",
    author_email="yousouf.taghzouti@inria.fr",
    url="https://github.com/Wimmics/t2s-metrics",
    licence="AGPL-3.0",
    license_files=["LICENSE"],
    keywords=[
        "Question Answering System",
        "Large Language Model",
        "Metric",
        "Text-to-SPARQL",
    ],
    python_requires=">=3.12",
)
