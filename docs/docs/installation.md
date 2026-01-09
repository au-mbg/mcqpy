# Installation

## Dependencies

- Python >= 3.13
- LaTeX (pdflatex and latexmk)

The Python package that `mcqpy` uses will be installed alongside `mcqpy` when installed with e.g. `pip` or `uv`.

## Installing LaTeX 

You will also need a working LaTeX installation, once `mcqpy` is installed you can check for that using 

```
mcqpy check-latex
```
Which will output the versions of `pdflatex` and `latexmk` if they are installed, if not you should install an OS 
appropriate LaTeX distribution for example from one of these sources: 

- **macOS**: [MacTeX](https://www.tug.org/mactex/)
- **Windows**: [TeX Live](https://www.tug.org/texlive/) or [MiKTeX](https://miktex.org/)
- **Linux**: TeX Live (usually available through your package manager, e.g., `sudo apt install texlive-full` on Ubuntu/Debian)

