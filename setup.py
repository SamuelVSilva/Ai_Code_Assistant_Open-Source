from setuptools import setup, find_packages

setup(
    name="ai-code-assistant",
    version="2.0.411012026",
    packages=find_packages(),
    install_requires=[
        "PyQt6>=6.5.0",
        "openai>=1.3.0",
        "anthropic>=0.7.0",
        "pyyaml>=6.0",
        "watchdog>=3.0.0"
    ],
    entry_points={
        'console_scripts': [
            'ai-code-assistant=src.main:main',
        ],
    },
    author="S Draeco Liliac",
    description="AI Code Assistant com múltiplos provedores",
    keywords="ai, code, assistant, development",
    python_requires=">=3.8",
)