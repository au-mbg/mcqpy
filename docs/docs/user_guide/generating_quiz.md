# Building a quiz

## Make a `mcqpy` project

The simplest way to start making a quiz is by using the 

```
mcqpy init <quiz_project_name>
```
command to make a quiz project directory, which produces a directory with this structure

```bash
./<quiz_project_name>
├── config.yaml
├── output/
├── questions/
└── submissions/
```

All relevant questions should be placed in the `questions/`-directory. 

## Configuring a quiz

Quiz settings are specified in the `config.yaml` file, which by default contains the following

```yaml
questions_paths:
- questions
file_name: quiz.pdf
root_directory: .
output_directory: output
submission_directory: submissions
front_matter:
  title: null  # Title of the quiz
  author: null # Author(s) of the quiz
  date: null   # Date written on the title page.
  exam_information: null # Additional information put on the title page of the quiz.
  id_fields: false # Whether or not to include name and number id-fields in the quiz.
header: # Header fields
  header_left: null 
  header_center: null
  header_right: Page \thepage \ of \ \pageref{LastPage}
  footer_left: null
  footer_center: null
  footer_right: null
selection: # Question selection/filtering fields
  number_of_questions: 20
  filters: null
  seed: null
  shuffle: false
  sort_type: none
```

## Building a quiz 

A quiz can be build using the command 

```
# Assuming that the terminal is in the quiz project directory
mcqpy build 
```

This produces three files
```
./output
├── quiz.pdf
├── quiz_manifest.json
└── quiz_solution.pdf
```

These are 

1. The quiz PDF which should be distributed to students. 
2. A quiz manifest that is required when grading
3. A solution document where each question has the correct answer(s) marked and if included in the question `.yaml`-file an explanation. 


