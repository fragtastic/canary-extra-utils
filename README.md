# canary-extra-utils

## Internal

- Create Factory Token(s) with `create_factory_token.sh`. See the file for usage.
- Prepare CSV/TSV from example.

## Enduser

- Install the requirements: `pip install -r requirements.txt`
- Get correct AWS profile name `grep -E -e "(\[.+\])" ~/.aws/credentials`
- Run the upload script:
  - `python create_tokens_s3.py --filename <csv or tsv file>`
  - `python -u create_tokens_s3.py --filename <csv or tsv file> | tee output.log`
