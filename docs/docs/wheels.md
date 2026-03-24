# Wheels

This page documents the temporary wheel publishing path used for browser-based
Shinylive testing before a PyPI release is cut.

Built wheels are copied into the documentation site under:

- `/wheels/`

The intended use is to reference a concrete `.whl` URL from Shinylive
`requirements.txt`, for example:

```text
https://au-mbg.github.io/mcqpy/wheels/mcqpy-0.2.4-py3-none-any.whl
```

Current example wheel:

- [`mcqpy-0.2.4-py3-none-any.whl`](/wheels/mcqpy-0.2.4-py3-none-any.whl)

This path is temporary and exists only to validate the hosted-wheel integration.
