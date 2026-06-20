"""
ai/prompts/__init__.py — AI Prompt Templates

Stores all prompt templates used for LLM-based evaluation (future capability).
Currently stubbed with template strings for when OpenAI/Gemini integration
is added without requiring domain or application layer changes.

Design:
  - Templates use Python .format() style placeholders.
  - Each prompt is a module-level constant for easy auditing and versioning.
  - Prompt versioning: bump PROMPT_VERSION when any template changes.
"""

PROMPT_VERSION: str = "1.0.0"
