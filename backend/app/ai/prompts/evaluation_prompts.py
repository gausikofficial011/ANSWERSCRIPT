"""
ai/prompts/evaluation_prompts.py — LLM Evaluation Prompt Templates

Prompt templates for LLM-based answer evaluation (future capability).
When OpenAI/Gemini integration is added, these templates are loaded
by a new LLMEvaluationAdapter without changing any use case logic.
"""

# ── Semantic Evaluation Prompt ────────────────────────────────────────────────

SEMANTIC_EVALUATION_PROMPT: str = """
You are an expert academic evaluator. Evaluate the student's answer against
the model answer for the question below.

Question: {question_text}

Model Answer: {model_answer}

Student Answer: {student_answer}

Maximum Marks: {max_marks}
Language: {language}

Evaluation Criteria:
1. Conceptual correctness and completeness
2. Coverage of key concepts from the model answer
3. Accuracy of facts and statements
4. Clarity and coherence of explanation

Respond with a JSON object in this exact format:
{{
  "score": <float between 0.0 and {max_marks}>,
  "percentage": <float between 0.0 and 100.0>,
  "feedback": "<one or two sentences explaining the score>",
  "key_concepts_covered": ["<concept1>", "<concept2>"],
  "key_concepts_missing": ["<concept1>", "<concept2>"]
}}

Respond with ONLY the JSON object. No explanation outside the JSON.
"""

# ── Keyword Extraction Prompt ─────────────────────────────────────────────────

KEYWORD_EXTRACTION_PROMPT: str = """
Extract the key technical terms and concepts from the following model answer.

Model Answer: {model_answer}
Subject: {subject_name}
Language: {language}

Return a JSON array of keywords/phrases:
["keyword1", "keyword2", "phrase with spaces"]

Include only domain-specific terms essential for a correct answer.
Exclude generic words (the, is, and, etc.).
Limit to maximum 15 keywords.
"""

# ── Feedback Generation Prompt ────────────────────────────────────────────────

FEEDBACK_GENERATION_PROMPT: str = """
Generate constructive academic feedback for a student answer.

Question: {question_text}
Student Answer: {student_answer}
Score Awarded: {score} / {max_marks}
Missing Concepts: {missing_concepts}

Write 2-3 sentences of constructive feedback in {language}.
Be encouraging but specific about what was missing or incorrect.
Do not repeat the question or score in your feedback.
"""
