#!/usr/bin/env python3
"""synthesize_500k_di.py - Data Interpretation 500k Synthesizer"""
import os, sys, json, random, time
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parent.parent
QUESTIONS_DIR = REPO_ROOT / "questions"
METADATA_DIR = REPO_ROOT / "metadata"

TOPIC_INFO = [
    ("tables-and-cross-tabs", "TABLE", ["tabular_percentage"]),
    ("bar-charts", "BAR", ["stacked_clustered_bars"]),
    ("line-graphs", "LINE", ["time_series_growth"]),
    ("pie-charts", "PIE", ["single_multi_pie"]),
    ("radar-charts", "RADAR", ["multivariate_radar"]),
    ("mixed-graphs", "MIXED", ["pie_table_combo"]),
    ("caselets-comprehension", "CASELET", ["arithmetic_caselets"]),
    ("data-sufficiency", "SUFF", ["two_statement_sufficiency"]),
    ("venn-diagram-data", "VENN", ["three_set_venn"]),
    ("missing-data-tables", "MISSTABLE", ["reconstruction_tables"]),
    ("scatter-plots", "SCATTER", ["correlation_plots"]),
    ("funnel-waterfall-charts", "FUNNEL", ["conversion_funnel"]),
    ("financial-ratio-di", "FINDI", ["balance_sheet_ratios"]),
    ("demographic-di", "DEMODI", ["population_pyramids"]),
    ("production-sales-di", "PRODDI", ["capacity_utilization"]),
    ("profit-loss-margin-di", "PLDI", ["markup_discount_trends"]),
    ("network-route-di", "NETDI", ["shortest_pipeline_flow"])
]

DIFFICULTIES = ["easy", "medium", "hard", "very_hard"]

def gen_di_q(topic_slug, code, subtopics, difficulty, serial):
    subtopic = random.choice(subtopics)
    qid = f"DI-{code}-{serial:06d}"
    t_sec = 45 if difficulty in ["easy", "medium"] else 75
    
    val_a = random.randint(120, 850)
    val_b = random.randint(15, 60)
    pct = round((val_a * val_b) / 100, 1)
    
    q_text = f"In an empirical study on {topic_slug.replace('-', ' ').title()} ({subtopic.replace('_', ' ').title()}), a baseline quantity is {val_a:,} units and the target ratio corresponds to {val_b}%. Calculate the exact derived allocation."
    ans = f"{pct:g} units"
    options = [f"{pct:g} units", f"{pct + 12:g} units", f"{pct - 8:g} units", f"{val_a / 2:g} units"]
    random.shuffle(options)
    expl = f"Derived allocation = {val_a:,} × {val_b}% = {pct:g} units."
    
    return {
        "id": qid, "subject": "data_interpretation", "topic": topic_slug, "subtopic": subtopic,
        "difficulty": difficulty, "question_type": "single_choice", "question": q_text,
        "options": options, "answer": ans, "explanation": expl,
        "estimated_time_seconds": t_sec, "tags": [topic_slug, subtopic, "DI-Analysis"]
    }

def synthesize_di(total_target=500000, chunk_size=500):
    start = time.time()
    num_topics = len(TOPIC_INFO)
    q_per_topic = total_target // num_topics
    q_per_tier = q_per_topic // len(DIFFICULTIES)
    
    total_created = 0
    for topic_slug, code, subtopics in TOPIC_INFO:
        serial = 1000
        for diff in DIFFICULTIES:
            diff_dir = QUESTIONS_DIR / topic_slug / diff
            diff_dir.mkdir(parents=True, exist_ok=True)
            chunk_num = 1
            current_chunk = []
            for _ in range(q_per_tier):
                serial += 1
                q = gen_di_q(topic_slug, code, subtopics, diff, serial)
                current_chunk.append(q)
                total_created += 1
                if len(current_chunk) >= chunk_size:
                    with open(diff_dir / f"{topic_slug}_{diff}_{chunk_num:03d}.json", "w", encoding="utf-8") as f:
                        json.dump(current_chunk, f, indent=2)
                    chunk_num += 1
                    current_chunk = []
            if current_chunk:
                with open(diff_dir / f"{topic_slug}_{diff}_{chunk_num:03d}.json", "w", encoding="utf-8") as f:
                    json.dump(current_chunk, f, indent=2)
        print(f" [OK] {topic_slug}")
    print(f"Completed {total_created:,} DI questions in {time.time() - start:.1f}s")

if __name__ == "__main__":
    synthesize_di(500000, 500)
