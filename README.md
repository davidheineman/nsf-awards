Dataset of 500K NSF awards. Last pulled May 2025.

Data includes with titles, abstracts and metadata, from 1960-present. Data is originally from https://www.nsf.gov/awardsearch/download.jsp, and is hosted on HF.

**Note:** Awards prior to 1976 are not fully included, and do not have all fields filled-in.

### Quick Start

```python
import pandas as pd
from datasets import load_dataset

dataset = load_dataset("davidheineman/nsf-awards")
df = pd.DataFrame(dataset['train'])

print(df.head(3))
```

### Setup

```sh
git clone https://github.com/davidheineman/nsf-awards
pip install -r requirements.txt

# Only pull 2025 data
python download.py --repo davidheineman/nsf-awards --min-year 2025
```