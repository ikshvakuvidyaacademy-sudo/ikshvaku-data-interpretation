#!/usr/bin/env python3
"""
generate_random_exam.py - Ikshvaku Random Exam Generator (Data Interpretation)
"""

import os, sys, json, random, argparse
from pathlib import Path
from typing import List, Dict, Any, Optional

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parent.parent
QUESTIONS_DIR = REPO_ROOT / "questions"


class RandomExamEngine:
    def __init__(self, questions_dir: Optional[Path] = None):
        self.questions_dir = questions_dir or QUESTIONS_DIR

    def get_candidate_files(self, topics=None, difficulties=None) -> List[Path]:
        all_files = []
        for topic_dir in self.questions_dir.iterdir():
            if not topic_dir.is_dir() or (topics and topic_dir.name not in topics):
                continue
            for diff_dir in topic_dir.iterdir():
                if not diff_dir.is_dir() or (difficulties and diff_dir.name not in difficulties):
                    continue
                all_files.extend(diff_dir.glob("*.json"))
        return all_files

    def select_random_questions(self, count=25, topics=None, difficulties=None) -> List[Dict[str, Any]]:
        candidate_files = self.get_candidate_files(topics=topics, difficulties=difficulties)
        if not candidate_files:
            return []

        shuffled_files = list(candidate_files)
        random.shuffle(shuffled_files)

        pool = []
        needed_pool_size = max(count * 5, 2000)

        for cf in shuffled_files:
            try:
                with open(cf, "r", encoding="utf-8") as f:
                    chunk = json.load(f)
                if isinstance(chunk, list):
                    pool.extend(chunk)
                if len(pool) >= needed_pool_size:
                    break
            except Exception:
                pass

        if not pool:
            return []

        selected = random.sample(pool, min(count, len(pool)))

        # Dynamic option shuffling
        processed = []
        for q in selected:
            q_copy = dict(q)
            if q_copy.get("question_type") == "single_choice" and isinstance(q_copy.get("options"), list):
                shuffled_options = list(q_copy["options"])
                random.shuffle(shuffled_options)
                q_copy["options"] = shuffled_options
            processed.append(q_copy)

        random.shuffle(processed)
        return processed

    def generate_blueprint_exam(self, blueprint: Dict[str, int], topics=None) -> List[Dict[str, Any]]:
        exam_questions = []
        for diff, count in blueprint.items():
            diff_sample = self.select_random_questions(count=count, topics=topics, difficulties=[diff])
            exam_questions.extend(diff_sample)
        random.shuffle(exam_questions)
        return exam_questions


def export_markdown_paper(questions: List[Dict[str, Any]], title: str, out_file: Path):
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(f"# 🏛️ Ikshvaku Aptitude Arena\n")
        f.write(f"### {title}\n")
        f.write(f"**Total Questions:** {len(questions)} | **Subject:** Data Interpretation & Data Sufficiency\n")
        tot_time = sum(q.get("estimated_time_seconds", 60) for q in questions) / 60
        f.write(f"**Recommended Time Limit:** {tot_time:.0f} Minutes\n\n---\n\n")

        for idx, q in enumerate(questions, 1):
            f.write(f"#### Q{idx}. [{q['id']}] ({q['topic'].replace('-', ' ').title()} - {q['difficulty'].upper()})\n\n")
            f.write(f"{q['question']}\n\n")
            if q.get("options"):
                labels = ["A", "B", "C", "D", "E"]
                for l, opt in zip(labels, q["options"]):
                    f.write(f"- **({l})** {opt}\n")
            f.write("\n")


def main():
    parser = argparse.ArgumentParser(description="Generate random exams from DI question bank.")
    parser.add_argument("--count", type=int, default=25, help="Total random questions (default: 25)")
    parser.add_argument("--blueprint", type=str, default=None, help="Difficulty quotas e.g. 'easy:10,medium:10,hard:5'")
    parser.add_argument("--topics", nargs="+", default=None, help="Filter by specific topics")
    parser.add_argument("--title", type=str, default="Ikshvaku Aptitude Arena - Data Interpretation Test", help="Exam Title")
    parser.add_argument("--output-dir", type=str, default="generated_exams", help="Output directory")
    args = parser.parse_args()

    engine = RandomExamEngine()
    print("=" * 80)
    print(" IKSHVAKU APTITUDE ARENA - DI RANDOM EXAM ENGINE")
    print("=" * 80)

    if args.blueprint:
        bp = {}
        for pair in args.blueprint.split(","):
            d, c = pair.strip().split(":")
            bp[d.strip().lower()] = int(c.strip())
        questions = engine.generate_blueprint_exam(bp, topics=args.topics)
    else:
        questions = engine.select_random_questions(count=args.count, topics=args.topics)

    print(f" Selected Questions: {len(questions)} unique random questions")
    out_dir = REPO_ROOT / args.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Student Paper
    student_paper = [{
        "id": q["id"], "topic": q["topic"], "difficulty": q["difficulty"],
        "question": q["question"], "options": q.get("options", []),
        "estimated_time_seconds": q.get("estimated_time_seconds")
    } for q in questions]

    with open(out_dir / "student_exam_paper.json", "w", encoding="utf-8") as f:
        json.dump({"exam_title": args.title, "total_questions": len(student_paper), "questions": student_paper}, f, indent=2)

    # 2. Instructor Key
    with open(out_dir / "instructor_answer_key.json", "w", encoding="utf-8") as f:
        json.dump({"exam_title": args.title, "solutions": questions}, f, indent=2)

    # 3. Printable Markdown Paper
    export_markdown_paper(questions, args.title, out_dir / "exam_paper.md")

    print(f" [SUCCESS] Generated in {out_dir}")
    print("=" * 80)


if __name__ == "__main__":
    main()
