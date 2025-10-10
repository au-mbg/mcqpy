from mcqpy.create.manifest import Manifest
from pathlib import Path
from pypdf import PdfReader

from dataclasses import dataclass
import numpy as np


@dataclass
class ParsedQuestion:
    qid: str
    slug: str
    answers: list[int]
    onehot: list[int]


@dataclass
class ParsedSet:
    student_id: str
    student_name: str
    questions: list[ParsedQuestion]


class MCQGrader:
    def __init__(self, manifest: Manifest, student_answer: str | Path):
        self.manifest = manifest
        self.student_answer = student_answer        

    ############################################################################
    # Parse the student answer PDF
    ############################################################################

    def _read_student_answer(self) -> str:
        reader = PdfReader(self.student_answer)

        split_by_id = self._split_by_id(reader.get_fields())
        student_name, student_id = self._find_student_info(reader.get_fields())
        parsed_questions = self._parse_questions(split_by_id)

        # Make ParsedQuestion objects
        parsed_set = ParsedSet(
            student_id=student_id, student_name=student_name, questions=parsed_questions
        )

        return parsed_set
    
    def _split_by_id(self, fields):
        split_by_id = {}
        for name, field in fields.items():
            # Find the id in the field name
            qid_start = name.find("qid")
            if qid_start == -1:
                continue  # Not a question field, hopefully.

            qid = name[qid_start + 4 :]  # +4 to skip 'qid='

            if qid not in split_by_id:
                split_by_id[qid] = [(name, field)]
            else:
                split_by_id[qid].append((name, field))
        return split_by_id

    def _find_student_info(self, fields):
        student_name = None
        student_id = None
        for name, field in fields.items():
            if name == "studentname":
                student_name = field.get("/V")
            elif name == "studentid":
                student_id = field.get("/V")

        if student_name is None or student_id is None:
            raise ValueError("Could not find student name or ID in the PDF fields.")

        return student_name, student_id

    def _parse_questions(self, split_by_id):
        parsed = []
        for qid, entries in split_by_id.items():
            slug = None
            answers = []
            onehot = []
            for name, field in entries:
                # Find the slug in the field name
                slug_start = name.find("slug")
                if slug_start != -1:
                    slug = name[slug_start + 5 :]  # +5 to skip 'slug='

                # Find the answer index in the field name
                opt_start = name.find("opt")
                if opt_start != -1:
                    opt_str = name[opt_start + 4 :].split("-")[0]  # +4 to skip 'opt='
                    try:
                        opt_index = int(opt_str)
                        if field.get("/V") == "/Yes":
                            answers.append(opt_index)
                            onehot.append(1)
                        else:
                            onehot.append(0)
                    except ValueError:
                        continue

            parsed.append(
                ParsedQuestion(qid=qid, slug=slug, answers=answers, onehot=onehot)
            )

        return parsed
    
    ############################################################################
    # Grade the parsed student answers
    ############################################################################

    def grade(self):
        parsed_set = self._read_student_answer()

        for parsed_question in parsed_set.questions:
            manifest_item = self.manifest.get_item_by_qid(parsed_question.qid)
            if manifest_item is None:
                print(f"Warning: No manifest item found for qid {parsed_question.qid}")
                continue

            # Grade the question
            print('Grading question:', parsed_question.qid)
            print(f'\t Student onehot: {parsed_question.onehot}')
            print(f'\t Correct onehot: {manifest_item.correct_onehot}')

            score = np.sum(np.array(parsed_question.onehot) == np.array(manifest_item.correct_onehot))
            print(f'\t Score: {score} out of {len(manifest_item.correct_onehot)}')





