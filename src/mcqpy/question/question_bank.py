import numpy as np
from mcqpy.question import Question
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class BankItem:
    question: Question
    path: Path


class QuestionBank:
    def __init__(self, items: list[BankItem], seed: int | None = None):
        self._items = items
        self._by_slug = {it.question.slug: it for it in items}
        self._by_qid  = {it.question.qid: it for it in items}
        self._rng = np.random.default_rng(seed=seed)

    @classmethod
    def from_directories(
        cls, directories: list[str], glob_pattern="*.yaml"):
        items = []
        qids, slugs = set(), set()
        for directory in directories:
            p = Path(directory)
            for file_path in p.glob(glob_pattern):
                question = Question.load_yaml(file_path)

                if question.slug in slugs:
                    raise ValueError(f"Duplicate slug found: {question.slug - {file_path}}")
                if question.qid in qids:
                    raise ValueError(f"Duplicate qid found: {question.qid - {file_path}}")
                
                slugs.add(question.slug)
                qids.add(question.qid)
                items.append(BankItem(question, file_path))

        return cls(items=items)
    
    def get_by_slug(self, slug: str) -> Question:
        if slug not in self._by_slug:
            raise KeyError(f"Slug {slug} not found in question bank")
        return self._by_slug[slug].question
    
    def get_by_qid(self, qid: str) -> Question:
        if qid not in self._by_qid:
            raise KeyError(f"QID {qid} not found in question bank")
        return self._by_qid[qid].question
    
    def get_all_questions(self) -> list[Question]:
        return [item.question for item in self._items]
