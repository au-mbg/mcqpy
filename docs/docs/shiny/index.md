# Web App 

`mcqpy` supports a web-interface through a Shinylive app.

## Embedding a quiz in a static site

The simplest usage is through `Quarto` where these steps will embed a 
quiz in a static site

1. Use the `shinylive` Quarto extension, see [github](https://github.com/quarto-ext/shinylive). 
2. Ensure the `shinylive` filter is activated for the appropriate files 
    ```
    filters:
      - shinylive
    ```
3. Embed the quiz with the block 

    ````
    ```{shinylive-python}
    #| standalone: true
    #| viewerHeight: 1200
    ## file: app.py
    from mcqpy_shiny.embed_app import create_app

    app = create_app(
        fixed_url=None,
        fixed_token=None,
        allow_manual_load=True,
        title='Quiz',
        card_width='900px',
    )
    ## file: requirements.txt
    shiny>=1.2.1
    pydantic
    mcqpy-core
    mcqpy-shiny
    ```
    ````

## Making a web quiz-bundle

The Shinylive app needs to read the quiz data from somewhere. The command 

```sh
mcqpy export web 
```
works similarly to `mcqpy build` but rather than producing a PDF based on a `config.yaml` it will produce web-bundle which is just a directory and a `.json`-file
```
- quiz.json
- assets/
```
Those need to be hosted on some publicly available site (like a GitHub repo) and 
the link to the `quiz.json` is what is provided to the app. 

Using either of the two arguments `fixed_url` and `fixed_token` provide ways of setting up a quiz 
with a specific bundle and if neither is given the app will start by asking for a token or a link. 

A token can be created using 

```sh
mcqpy export encode-token <URL> 
```
This is only intended to slightly obfuscate the origin of the quiz bundle (e.g. to avoid students finding the repo). 
