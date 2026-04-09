from dataclasses import dataclass
from enum import Enum

@dataclass
class ParsedQuestion:
    qid: str
    slug: str
    answers: list[int]
    onehot: list[int]


@dataclass
class ParsedSet:
    student_info: dict[str, str]
    questions: list[ParsedQuestion]
    file: str | None = None


@dataclass
class GradedQuestion:
    qid: str
    slug: str
    student_answers: list[int]
    correct_answers: list[int]
    max_point_value: int
    point_value: int = 0


@dataclass
class GradedSet:
    student_info: dict[str, str]
    graded_questions: list[GradedQuestion]
    points: int = 0
    max_points: int = 0

class ParseState(Enum):
    READER_ERROR = "Error reading PDF file. The file may be corrupted or not a valid PDF."
    SUCCESS = "Successfully parsed PDF file."

class GradeState(Enum):
    READER_ERROR = ParseState.READER_ERROR.value
    SUCCESS = "Successfully graded the parsed set."

@dataclass
class ParseResult:
    state: ParseState
    parsed_set: ParsedSet | None = None
    error_message: str | None = None
    other_info: dict | None = None

@dataclass
class GradeResult:
    state: GradeState
    graded_set: GradedSet | None = None
    error_message: str | None = None
    other_info: dict | None = None