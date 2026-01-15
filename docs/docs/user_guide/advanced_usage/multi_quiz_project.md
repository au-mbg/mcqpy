# Multi Quiz Project

It can often be convenient to organize multiple quizzes into a single project 
that use a shared bank of questions. 

## Project setup

For this type of project a directory structure like so can be recommended: 

```bash
multi_quiz_project/
├── configs/
│  ├── chapter_1.yaml
│  └── chapter_2.yaml
├── generated_quizzes/
│  ├── chapter_1/
│  │  ├── output
│  │  └── submissions
│  ├── chapter_2/
│  │  ├── output
│  │  └── submissions
├── questions/
│  └── images/
```

## Configuration file(s)

Each quiz has a configuration file, an example is shown below

```yaml
questions_paths:
- ../questions # Relative to the localtion of the config file
root_directory: ../generated_quizzes/chapter_1/ # Relative to the location of the config file.
file_name: chapter_1_quiz.pdf
output_directory: output/ # Relative to root_directory
grading:
  submission_directory: submissions/ # Relative to root directory
front_matter:
  title: Chapter 1 Quiz
  author: null
  date: null
  exam_information: null
  id_fields: true
header:
  header_left: null
  header_center: Chapter 1
  header_right: Page \thepage \ of \ \pageref{LastPage}
  footer_left: null
  footer_center: null
  footer_right: null
selection:
  number_of_questions: null
  sort_type: slug
  shuffle: False
  filters: {
    tag: {
      tags: ['chapter_01']
    },   
  }
```

With this configuration file a quiz including only those questions that have been tagged `chapter_01`
can be generated using
```
mcqpy build -c configs/chapter_1.yaml
```

## Filters

`mcqpy` offers various filters to customize question selection

- `tag`: For filtering based on tags.
- ´date`: For filtering based on dates or date intervals.
- `difficulty`: For filtering based on question difficulty.
- `stratified`: Stratified selection, e.g. to select a, roughly, equal amount of questions from chapter 1 and chapter 2. 
- `manifest`: Exclude questions used in a previous quiz. 

If multiple filters are specified in the `config.yaml`-file they will be applied sequentially. 
Filters are specified as dictionary in the `filter-dictionary` of the `config.yaml`, the general 
syntax is

```yaml
filters: {
    filter_type_1: {
        arg_name_1: <some_argument>,
        arg_name_2: <other_argument>
    },   
    filter_type_2: {
        arg_name_1: ..., 
        arg_name_2: ...
    }
}
```
where `filter_type_1` needs to be one of `tag`, `date`, `stratified´, `difficulty` or `manifest` 
and the arguments depend on which one.

### Tag filtering

The syntax for tag filtering is 

```yaml
filters: {
tag: {
    tags: [tag1, tag2], # list[str]: Tags to consider.
    match_all: false, # optional bool: If true all tags must match.
    exclude: false,  # optional bool: If true questions are excluded rather than included.
    strict_missing: true # optional bool: If true questions without tags are discarded. 
    },   
}
```

### Date Filtering

The syntax for date filtering is

```yaml
filters: {
date: {
    date_value: <operator>dd/mm/yyyy, # str: Date where operator can be one of ['<=', '>=', '<', '>']
    end_date: dd/mm/yyyy, # optional str
    strict_missing: true # bool: If true questions without dates are discarded. 
    },   
}
```

### Difficulty Filtering

The syntax for difficulty filtering is

```yaml
filters: {
difficulty: {
    difficulty: <operator><difficulty>, # str: One of ['very easy', 'easy', 'medium', 'hard', 'very hard']
    operator: '==', # str: One of ['==', '<', '<=', '>', '>=']
    strict_missing: true # bool: If true questions without difficulty are discarded. 
    },   
}
```
The operator can also be specified as part of the difficulty string, for example `>easy`. 

### Stratified filtering

The `stratified`-filter combines several of the other filters types and picks according 
to specified proportions, the syntax is 

```yaml
filters: {
    stratified: {
        'number_of_questions': 30,
        'filter_configs': [
            {'type': 'tag', 'tags': ['chapter_01']},
            {'type': 'tag', 'tags': ['chapter_02']},
        ],
        'proportions': [1, 2]
        }
}
```
Where `filter_configs` is is a `dict` with the type and keyword arguments for the filters
and `proportions` specifies the the proportions of questions selected based on each filter. 
In the above example $1/3$ will be picked among those questions that are tagged `chapter_01`
and $2/3$ will be picked from those tagged `chapter_02`.

### Manifest filtering

Manifest filtering is intended to be used to make sure questions are not reused, 
for example to ensure exam questions used in one year are not used in another year. 
The syntax is

```yaml
filters: {
    manifest: {
      manifest_path: <path/to/previous/manifest.json>, # Path to manifest file.
      exclude: true # Bool: Whether to exlucde or include the questions specified in the manifest.
      },
}
```

### Checking filters

`mcqpy` offers a utility CLI command to check that filter specifications are correct

```
mcqpy utils check-filter -c <path/config.yaml> 
```

Or 

```
mcqpy utils check-filter -y "<raw yaml>"
```

Or 

```
mcqpy utils check-filter -fn <filter_name> -fp "<filter_parameters_yaml>"
```

## Grading 

Grading works the same way as for a single quiz, except that the path to the corresponding 
`config.yaml`-file should be specified 

```
mcqpy grade -c <path/config.yaml> -a
```


