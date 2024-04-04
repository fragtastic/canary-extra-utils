# canary-extra-utils

- Install the requirements: `pip install -r requirements.txt`
- Create Factory Token(s) with `create_factory_token.sh`. See the file for usage.
- Prepare CSV from example.
- Run the upload script:
  - `python create_tokens_s3.py --filename <csv or tsv file>`
  - `python -u create_tokens_s3.py --filename <csv or tsv file> | tee example.log`
