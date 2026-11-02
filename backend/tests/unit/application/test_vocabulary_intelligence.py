import pytest
from app.infrastructure.ai.text_normalization_service import TextNormalizationService
from app.infrastructure.ai.synonym_dictionary_service import SynonymDictionaryService
from app.infrastructure.ai.keyword_evaluation_service import KeywordEvaluationService
from app.infrastructure.ai.score_aggregation_service import ScoreAggregationService


def test_text_normalization_lemmatizer():
    normalizer = TextNormalizationService()
    
    # 1. Singular/Plural singularization
    assert normalizer.lemmatize_word("veins") == "vein"
    assert normalizer.lemmatize_word("leaves") == "leaf"
    assert normalizer.lemmatize_word("orbits") == "orbit"
    
    # 2. Verb tenses
    assert normalizer.lemmatize_word("pumps") == "pump"
    assert normalizer.lemmatize_word("pumping") == "pump"
    assert normalizer.lemmatize_word("pumped") == "pump"
    assert normalizer.lemmatize_word("orbiting") == "orbit"
    assert normalizer.lemmatize_word("revolving") == "revolve"
    
    # 3. Tokenize & Clean
    tokens = normalizer.normalize_text("The heart pumps blood through our veins!")
    assert "heart" in tokens
    assert "pump" in tokens
    assert "vein" in tokens
    assert "blood" in tokens


def test_synonym_expansion():
    synonym_service = SynonymDictionaryService()
    
    # Test gravity synonyms
    gravity_syns = synonym_service.expand_keywords(["gravity"])
    assert "attractive force" in gravity_syns
    assert "gravitational force" in gravity_syns
    assert "gravity" in gravity_syns
    
    # Test orbit synonyms
    orbit_syns = synonym_service.expand_keywords(["orbit"])
    assert "orbiting" in orbit_syns
    assert "revolving" in orbit_syns
    assert "moving around" in orbit_syns


def test_keyword_matching_with_synonyms():
    evaluator = KeywordEvaluationService()
    
    # Expected: "gravity", Student: "The attractive force pulls objects."
    res_a = evaluator.evaluate_keywords(
        student_answer="The attractive force pulls objects.",
        expected_keywords=["gravity"]
    )
    assert res_a["keyword_score"] == 1.0
    assert "gravity" in res_a["matched_keywords"]
    
    # Expected: "pump blood", Student: "The cardiovascular heart pumps blood around the body."
    res_b = evaluator.evaluate_keywords(
        student_answer="The cardiovascular heart pumps blood around the body.",
        expected_keywords=["pump blood"]
    )
    assert res_b["keyword_score"] == 1.0
    assert "pump blood" in res_b["matched_keywords"]


def test_soft_semantic_gating():
    service = ScoreAggregationService()
    
    # 1. 0% keywords -> multiplier = 0.25 floor (previously zeroed out to 0.0)
    # Expected semantic: 40% Semantic, 60% Keyword
    # Gating threshold = 0.20
    # Expected: (0.40 * 8.0 * 0.25) + (0.60 * 0.0 * 10) = 0.8 + 0.0 = 0.80 marks
    res_a = service.aggregate_score(
        similarity_score=0.80, # 8.0 out of 10.0 max
        keyword_match_score=0.0,
        rubric_score=None,
        max_marks=10.0
    )
    assert res_a["final_score"] == 0.80

    # 2. 10% keyword match -> multiplier = 0.10 / 0.20 = 0.50 (max(0.25, 0.50) = 0.50)
    # Expected: (0.40 * 8.0 * 0.50) + (0.60 * 1.0) = 1.6 + 0.6 = 2.20 marks
    res_b = service.aggregate_score(
        similarity_score=0.80,
        keyword_match_score=0.10,
        rubric_score=None,
        max_marks=10.0
    )
    assert res_b["final_score"] == 2.20
