from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="nova-lang",
    version="0.0.0.1",
    author="Nova Language Team",
    author_email="nova@example.com",
    description="A world-class, web-development focused programming language with built-in AI capabilities.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/authorss81/Nova",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    entry_points={
        "console_scripts": [
            "nova=nova.__main__:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)