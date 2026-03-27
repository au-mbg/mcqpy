# Wheels

This page documents the temporary wheel publishing path used for browser-based
Shinylive testing before a PyPI release is cut.

Built workspace wheels are copied into the documentation site under:

- `/wheels/`

The intended use is to reference a concrete `.whl` URL from Shinylive
`requirements.txt`, for example:

```text
https://au-mbg.github.io/mcqpy/wheels/mcqpy_shiny-0.1.1-py3-none-any.whl
```

The branch preview workflow publishes all current workspace wheels there:

- [`mcqpy-0.3.1-py3-none-any.whl`](/wheels/mcqpy-0.3.1-py3-none-any.whl)
- [`mcqpy_core-0.1.1-py3-none-any.whl`](/wheels/mcqpy_core-0.1.1-py3-none-any.whl)
- [`mcqpy_pdf-0.1.1-py3-none-any.whl`](/wheels/mcqpy_pdf-0.1.1-py3-none-any.whl)
- [`mcqpy_shiny-0.1.1-py3-none-any.whl`](/wheels/mcqpy_shiny-0.1.1-py3-none-any.whl)

This path is temporary and exists only to validate the hosted-wheel integration.
