"""
Quiz configuration management using Pydantic and YAML.
"""

from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator
import yaml
from mcqpy.compile import HeaderFooterOptions, FrontMatterOptions
from typing import Any, Literal
from pathlib import Path


class GradingConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)
    submission_directory: str = Field(
        default="submissions", description="Directory for student submissions relative to quiz root directory"
    )
    anonymous_pattern: str | None = Field(
        default=None,
        description="Regex pattern to extract identifiers from anonymous exam filenames (e.g., 'exam_(?P<id1>\\w+)_(?P<id2>\\w+)\\.pdf')",
    )
    output_sort_key: str | None = Field(
        default=None,
        description="Key to sort output files, e.g., 'student_name' or 'student_id' or one based on the anonymous pattern",
    )

    @field_validator("anonymous_pattern")
    @classmethod
    def validate_pattern(cls, v):
        """Validate that the pattern is a valid regex"""
        if v is not None:
            import re

            try:
                re.compile(v)
            except re.error as e:
                raise ValueError(f"Invalid regex pattern: {e}")
        return v


class SelectionConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)
    number_of_questions: int | None = Field(
        default=20, description="Number of questions to select"
    )
    filters: dict[str, dict[str, Any]] | None = Field(
        default=None, description="Filters to apply when selecting questions"
    )
    seed: int | None = Field(
        default=None, description="Random seed for question selection"
    )
    shuffle: bool = Field(
        default=False, description="Whether to shuffle selected questions"
    )
    sort_type: Literal["slug", "none"] = Field(
        default="none", description="Sort type for selected questions"
    )


class QuizConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True, populate_by_name=True)
    questions_paths_: list[str] | str = Field(
        default=["questions"], description="Paths to question files or directories, relative to the config file's directory", alias="questions_paths"
    )
    file_name: str = Field(
        default="quiz.pdf", description="Name of the output PDF file"
    )
    
    root_directory_: str = Field(
        default=".", description="Root directory for the quiz project, relative to the location of the config file", 
        alias="root_directory"
    )
    output_directory_: str = Field(
        default="output", description="Directory for output files, relative to the root directory", alias="output_directory"
    )
    grading: GradingConfig = Field(default_factory=GradingConfig)
    front_matter: FrontMatterOptions = Field(default_factory=FrontMatterOptions)
    header: HeaderFooterOptions = Field(default_factory=HeaderFooterOptions)
    selection: SelectionConfig = Field(default_factory=SelectionConfig)
    path: Path | None = Field(None, description="Internal: file path from which the config was loaded", exclude=True)

    @property
    def root_directory(self) -> Path:
        """Get root directory as a Path object"""
        return (Path(self.path).parent / self.root_directory_).resolve()
    
    @property
    def output_directory(self) -> Path:
        """Get output directory as a Path object"""
        return self.root_directory / self.output_directory_

    @property
    def questions_paths(self) -> list[Path]:
        """Get questions paths as Path objects"""
        return [self.root_directory / p for p in self.questions_paths_]
    
    @property
    def file_path(self) -> Path:
        """Get full file path for the output PDF"""
        return self.output_directory / self.file_name
    
    @property
    def submission_directory(self) -> Path:
        """Get submission directory as a Path object"""
        return self.root_directory / self.grading.submission_directory
    

    @model_validator(mode="before")
    @classmethod
    def migrate_submission_directory(cls, data):
        """Migrate submission_directory from top level to grading config"""
        if isinstance(data, dict) and "submission_directory" in data:
            if "grading" not in data:
                data["grading"] = {}
            data["grading"]["submission_directory"] = data.pop("submission_directory")
        return data
    
    @model_validator(mode="before")
    def check_paths_exist(cls, data):
        """Resolve questions_paths relative to the config file's directory"""
        path = data.get("path")
        if not path:
            return data
        
        config_dir = path.parent
        
        # Questions:
        paths_to_check = data.get("questions_paths", []) + data.get("questions_paths_", [])
        for path in paths_to_check:
            resolved_path = (config_dir / path).resolve()
            if not resolved_path.exists():
                raise FileNotFoundError(f"Questions path does not exist: {resolved_path}")

        return data

    def yaml_dump(self) -> str:
        """Dump the current configuration to a YAML string"""
        config_dict = self.model_dump(by_alias=True)
        yaml_content = yaml.dump(config_dict, default_flow_style=False, sort_keys=False)
        return yaml_content

    @classmethod
    def generate_example_yaml(cls) -> str:
        """Generate example YAML with comments"""
        example = cls()
        return example.yaml_dump()

    @classmethod
    def read_yaml(cls, file_path: str) -> "QuizConfig":
        """Read YAML file and return a QuizConfig instance"""
        with open(file_path, "r") as file:
            yaml_string = file.read()
        data = yaml.safe_load(yaml_string)
        data['path'] = Path(file_path).resolve()
        return cls(**data)
