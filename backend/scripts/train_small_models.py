"""
backend/scripts/train_small_models.py — Hardware-Aware Lightweight Model Trainer

Trains a CPU-bounded Logistic Regression + TF-IDF n-gram classifier for
cross-script pairwise plagiarism and collusion detection.
Saves model checkpoint to ml/models/plagiarism_v1.joblib.
"""

import os
import sys
import time
from pathlib import Path
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.pipeline import Pipeline

BASE_DIR = Path(__file__).resolve().parent.parent.parent


def get_training_corpus():
    """Generates synthetic academic pairs with labeled collusion status."""
    pairs = [
        # Collusive pairs (Label 1)
        (
            "ACID properties: Atomicity guarantees all or nothing. Consistency keeps DB valid. Isolation prevents conflicts. Durability saves data.",
            "ACID rules: Atomicity ensures all or nothing. Consistency keeps DB valid. Isolation stops conflicts. Durability persists changes.",
            1
        ),
        (
            "Process Control Block PCB stores process id, program counter, CPU registers, and scheduling information.",
            "PCB or Process Control Block holds process id, program counter, CPU register set, and process schedule info.",
            1
        ),
        (
            "Normalization reduces data redundancy by dividing large tables into smaller connected relations through foreign keys.",
            "Normalization eliminates redundancy by splitting big tables into smaller related tables using foreign key links.",
            1
        ),
        (
            "Prim's algorithm starts from an arbitrary node and repeatedly adds the minimum weight edge adjacent to visited vertices.",
            "Prim's algorithm begins at a starting node and greedily selects the minimum weight edge connected to visited nodes.",
            1
        ),
        # Non-collusive independent pairs (Label 0)
        (
            "ACID properties: Atomicity guarantees all or nothing. Consistency keeps DB valid. Isolation prevents conflicts. Durability saves data.",
            "The quick sort algorithm partitions an array using a pivot element and sorts sub-arrays recursively.",
            0
        ),
        (
            "Process Control Block PCB stores process id, program counter, CPU registers, and scheduling information.",
            "TCP is a connection-oriented transmission protocol that uses a three-way handshake for reliable delivery.",
            0
        ),
        (
            "Normalization reduces data redundancy by dividing large tables into smaller connected relations through foreign keys.",
            "Virtual memory uses paging and segmentation to map logical addresses to physical RAM frames.",
            0
        ),
        (
            "Prim's algorithm starts from an arbitrary node and repeatedly adds the minimum weight edge adjacent to visited vertices.",
            "Relational algebra operations include select, project, cartesian product, union, and set difference.",
            0
        ),
    ]

    texts = [f"{p[0]} [SEP] {p[1]}" for p in pairs]
    labels = [p[2] for p in pairs]
    return texts, labels


def train_plagiarism_classifier():
    print("=" * 65)
    print("    INTELLIGRADE LIGHTWEIGHT CPU CLASSIFIER TRAINER")
    print("=" * 65)
    start_time = time.time()

    texts, labels = get_training_corpus()

    # Define lightweight, CPU-efficient NLP pipeline
    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), max_features=1000, lowercase=True)),
        ("classifier", LogisticRegression(solver="liblinear", random_state=42))
    ])

    print(f"Training sample size: {len(texts)} document pairs")
    print("Feature extractor:    TF-IDF (unigram + bigram, max_features=1000)")
    print("Classification head:  Logistic Regression (L2 penalty, liblinear)")

    pipeline.fit(texts, labels)
    preds = pipeline.predict(texts)

    acc = accuracy_score(labels, preds)
    prec = precision_score(labels, preds)
    rec = recall_score(labels, preds)
    f1 = f1_score(labels, preds)
    duration = time.time() - start_time

    print(f"\nTraining Results ({duration:.3f}s):")
    print(f"  - Accuracy:  {acc * 100:.1f}%")
    print(f"  - Precision: {prec * 100:.1f}%")
    print(f"  - Recall:    {rec * 100:.1f}%")
    print(f"  - F1 Score:  {f1:.3f}")

    # Save artifact
    model_dir = BASE_DIR / "ml/models"
    model_dir.mkdir(parents=True, exist_ok=True)
    checkpoint_file = model_dir / "plagiarism_v1.joblib"
    joblib.dump(pipeline, checkpoint_file)
    print(f"\nModel checkpoint successfully written to: {checkpoint_file}")
    print("=" * 65)


if __name__ == "__main__":
    train_plagiarism_classifier()
