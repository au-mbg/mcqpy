# Grading quizzes

Finished quizzes can be graded based on the `*_manifest.json`-file produced during quiz generation. 

Assuming a `mcqpy` project with a structure like so (as produced by `mcqpy init`)

```bash
./<quiz_project_name>
├── config.yaml
├── output/
├── questions/
└── submissions/
```

Running the command 

```
mcqpy grade
```

Will grade the submissions in the `submissions/`-directory and produce a `.xlsx` or (`.csv` if the `-f csv` option is provided) containing 
the grades of the students. 

## Testing

`mcqpy` offers a utility tool to test grading without waiting for or manually creating 
submissions. 

```
mcqpy utils autofill -n 100
```

Will produce 100 randomly filled quizzes that can then be graded as above: 

```
mcqpy grade
```

## Question level statistics 

In addition to the tabular output `mcqpy` can also produce a more detailed report of the submisisons

```
mcqpy grade -a 
```

Which in addition to the `.xlsx` or `.csv` files also produces `analysis/quiz_analysis.pdf` which 
contains answer distribution for each question. 

## Rubrics 

`mcqpy` currently only supports a single rubric for grading 

- `StrictRubric`: Points are only awarded for fully correct answers, both for single choice and multiple choice questions. 

This will likely be improved in the future.


