## Install

- Requires python 3.6+
```
pip install formulapy
```

## Usage

- process file : `formulapy file <filename> [--w]`

  **If `--w` is set, the file would be overwritten**.

- process text : `formulapy text <text>`

```
cmd> formulapy file test.py
from formulapy import tex

def Σ(arr):
    pass

cmd> formulapy text "tex[A,'cap',B,'cap',C]"
A∩B∩C
```

