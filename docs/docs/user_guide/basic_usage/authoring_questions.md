# Authoring Questions

## Question files

The basic unit of a `mcqpy` quiz is a quiz question which is a `yaml` file containing 
the fields of the question. 

A template of a question can be created by running the command 

```bash
mcqpy question init <filename_of_question.yaml>
```

Which produces a file that looks like so

```yaml
# Question Template (auto-generated from model schema)

# slug (Required)
# Immutable short key chosen at creation
slug: my-unique-question-slug

# text (Required)
# Question text, may contain LaTeX
text: Your question text here (LaTeX supported)

# choices (Required)
# Answer choices
choices:
- Answer choice 1
- Answer choice 2
- Answer choice 3
- Answer choice 4

# correct_answers (Required)
# Indices of correct answers in `choices`, 0-based
correct_answers:
- 0

# question_type (Required)
# Type of question: 'single' for single-choice, 'multiple' for multiple-choice
question_type: single

# image (Optional)
# Path(s) to image file(s) associated with the question
# image: path/to/image.png

# image_options (Optional)
# Options for image(s) display, e.g., width, height
# image_options:
#   0:
#     width: 0.5\textwidth

# image_caption (Optional)
# Caption(s) for each image(s), if any
# image_caption:
#   -1: Caption for all images

# code (Optional)
# Code snippet associated with the question
# code: print('Hello, world!')

# code_language (Optional)
# Programming language of the code snippet(s)
# code_language: python

# point_value (Optional)
# Point value of the question
# point_value: 1

# difficulty (Optional)
# difficulty: medium

# tags (Optional)
# tags:
# - tag1
# - tag2

# explanation (Optional)
# explanation: Optional explanation of the correct answer

# created_date (Optional)
# Date question was created. Stored as 'dd/mm/yyyy' (input accepts 'yyyy' or 'dd/mm/yyyy')

# comment (Optional)
# Internal comment for instructors/editors
```

## Required fields

A few fields are required when authoring a question, these are 

- `slug`: A short unique, human-readable text describing the question.
- `text`: The text to render with the question, this can include LaTeX notation.
- `choices`: The possible choices for the question, again this can include LaTeX.
- `correct_answers`: One or more 0-based indices for the correct answer(s).
- `question_type`: Either "single" or "multiple" depending on if multiple choices may be selected. 

## Optional fields

In addition to the required fields, there are a number of optional fields 

- `image`: Paths, relative to the question `.yaml` file, or URLs for images to include with the question. 
- `image_options`: Dictionary of options for each image, most importantly `width` to control the size of the figure in the rendered document and `newline: true` to force a new row after that subfigure. The key for each entry is an integer, `0` for the first image and so on.
- `image_captions`: Dictionary of captions for each image. If there are multiple figures, the key `-1` is interpreted as the caption for whole figure while `0`, `1` etc are the captions for each subfigure. 
- `code`: A code-snippet or a list of code-snippets to render with the question.
- `code_language`: Code language or list of code languages for each snippet, used to control highlighting. 
- `point_value`: The point value of the question, defaults to 1, used when grading. This allows having questions that are worth more than others. 
- `difficulty`: The difficulty level of the question, used for filtering when building a quiz. Can be `very easy`, `easy`, `medium`, `hard` or `very hard`
- `tags`: List of keyword tags that may be used to filter questions during quiz generation.
- `explanation`: An explanation that will be included in the solution PDF document, supports LaTeX. 
- `created_date`: A date for when the question was created, used for filtering.
- `comment`: An optional comment about the question, not shown in any of the output documents. 

## Utilities 

`mcqpy` provides two utilities tools for making authoring questions easier. Firstly, 
the `.yaml`-file can be validated using 

```
mcqpy question validate <question_file_1.yaml> <question_file_2.yaml> ...
```
To check that all required fields have been filled and that all fields have the expected types/format and 
that referenced figures can be found. Secondly, a question can be rendered using 
```
mcqpy question render <question_file.yaml>
```
Which is useful to catch LaTeX errors prior to building a quiz with multiple questions. 
If successful a PDF containing just that question is produced. 



