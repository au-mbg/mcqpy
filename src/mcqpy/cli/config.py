from pydantic import BaseModel, Field, ConfigDict
import yaml
from mcqpy.create import HeaderFooterOptions, FrontMatterOptions

class QuizConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)
    questions_paths: list[str] | str = Field(default=["questions"], description="Paths to question files or directories")
    file_name: str = Field(default="quiz.pdf", description="Name of the output PDF file")
    output_directory: str = Field(default="output", description="Directory for output files")
    front_matter: FrontMatterOptions = Field(default_factory=FrontMatterOptions)
    header: HeaderFooterOptions = Field(default_factory=HeaderFooterOptions)

    def yaml_dump(self) -> str:
        """Dump the current configuration to a YAML string"""
        config_dict = self.model_dump()
        yaml_content = yaml.dump(config_dict, default_flow_style=False, sort_keys=False)
        return yaml_content

    @classmethod
    def generate_example_yaml(cls) -> str:
        """Generate example YAML with comments"""
        example = cls()
        return example.yaml_dump()