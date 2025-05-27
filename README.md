Dataset of 500K NSF awards with titles, abstracts and metadata, from 1960-present. Data is originally from https://www.nsf.gov/awardsearch/download.jsp. Last pulled May 2025.

Awards prior to 1976 are not fully included, and do not have all fields filled-in.

```sh
# Only pull 2025 data
python download.py --repo davidheineman/nsf-awards --min-year 2025
```