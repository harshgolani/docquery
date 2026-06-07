"""
Custom RAG evaluation suite for Docquery.
Scores faithfulness and answer relevancy using Claude as the judge.
No external eval frameworks — works with Python 3.13.

Metrics:
  Faithfulness     — is the answer grounded in the retrieved context?
  Answer Relevancy — does the answer address the question asked?

Usage:
    cd backend/evals
    python eval.py

Output: eval_results.json
"""

import os
import sys
import json
import anthropic

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from rag import ingest_document, query_document, delete_document

TEST_DOC_ID   = "eval_test_doc"
TEST_PDF_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test.pdf")
JUDGE_MODEL   = "claude-haiku-4-5"

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

TEST_CASES = [
    {"question": "When was Anthropic founded?",
     "ground_truth": "Anthropic was founded in 2021."},
    {"question": "What is Claude?",
     "ground_truth": "Claude is a large language model assistant and Anthropic's flagship product."},
    {"question": "What are the versions of Claude?",
     "ground_truth": "Claude is available in Haiku, Sonnet, and Opus versions."},
    {"question": "How much does Claude Haiku cost?",
     "ground_truth": "Claude Haiku costs $0.25 per million input tokens."},
    {"question": "How much does Claude Sonnet cost?",
     "ground_truth": "Claude Sonnet costs $3 per million input tokens."},
    {"question": "How much does Claude Opus cost?",
     "ground_truth": "Claude Opus costs $15 per million input tokens."},
    {"question": "Where is Anthropic headquartered?",
     "ground_truth": "Anthropic is headquartered in San Francisco, California."},
    {"question": "What does Anthropic focus on?",
     "ground_truth": "Anthropic focuses on building reliable, interpretable, and steerable AI systems."},
    {"question": "Which Claude model is the fastest?",
     "ground_truth": "Haiku is the fastest and most compact model."},
    {"question": "Which Claude model is most capable for complex tasks?",
     "ground_truth": "Opus is the most capable model for complex tasks."},
]

def score_faithfulness(question, answer, contexts):
    context_text = "\n\n---\n\n".join(contexts)
    prompt = f"""You are evaluating a RAG system. Score whether the answer is faithful to the context.

QUESTION: {question}

CONTEXT:
{context_text}

ANSWER: {answer}

Score:
- 1.0: Every claim is directly supported by the context
- 0.5: Most claims are supported but some are not
- 0.0: Answer contains claims not supported by the context

Respond with ONLY a number: 1.0, 0.5, or 0.0"""

    response = client.messages.create(
        model=JUDGE_MODEL, max_tokens=10,
        messages=[{"role": "user", "content": prompt}]
    )
    try:
        return float(response.content[0].text.strip())
    except ValueError:
        return 0.5


def score_relevancy(question, answer):
    prompt = f"""You are evaluating a RAG system. Score whether the answer addresses the question.

QUESTION: {question}

ANSWER: {answer}

Score:
- 1.0: Directly and completely addresses the question
- 0.5: Partially addresses the question
- 0.0: Does not address the question

Respond with ONLY a number: 1.0, 0.5, or 0.0"""

    response = client.messages.create(
        model=JUDGE_MODEL, max_tokens=10,
        messages=[{"role": "user", "content": prompt}]
    )
    try:
        return float(response.content[0].text.strip())
    except ValueError:
        return 0.5


def main():
    print(f"Ingesting: {TEST_PDF_PATH}")
    with open(TEST_PDF_PATH, "rb") as f:
        chunks = ingest_document(TEST_DOC_ID, "test.pdf", f.read())
    print(f"Ingested {chunks} chunks\n")

    results = []
    faithfulness_scores = []
    relevancy_scores = []

    for i, tc in enumerate(TEST_CASES):
        print(f"[{i+1}/{len(TEST_CASES)}] {tc['question']}")
        response = query_document(TEST_DOC_ID, tc["question"])
        answer = response["answer"]
        contexts = response["sources"]

        f_score = score_faithfulness(tc["question"], answer, contexts)
        r_score = score_relevancy(tc["question"], answer)

        faithfulness_scores.append(f_score)
        relevancy_scores.append(r_score)
        print(f"  Faithfulness: {f_score}  |  Relevancy: {r_score}")

        results.append({
            "question": tc["question"],
            "ground_truth": tc["ground_truth"],
            "answer": answer,
            "contexts": contexts,
            "faithfulness": f_score,
            "answer_relevancy": r_score,
        })

    avg_f = round(sum(faithfulness_scores) / len(faithfulness_scores), 4)
    avg_r = round(sum(relevancy_scores) / len(relevancy_scores), 4)

    print("\n" + "="*50)
    print("EVAL RESULTS")
    print("="*50)
    print(f"  Faithfulness:     {avg_f}")
    print(f"  Answer Relevancy: {avg_r}")
    print("="*50)

    output = {
        "scores": {"faithfulness": avg_f, "answer_relevancy": avg_r},
        "n": len(TEST_CASES),
        "model": JUDGE_MODEL,
        "results": results,
    }

    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "eval_results.json")
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nSaved to {out_path}")


if __name__ == "__main__":
    try:
        main()
    finally:
        delete_document(TEST_DOC_ID)
        print("Cleaned up test collection.")
