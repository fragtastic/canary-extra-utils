import csv
import json
import requests
import pathlib
import os
import re
import time
import boto3
import argparse


allowedTokenTypes = ['aws-id', 'doc-msword', 'msexcel-macro', 'msword-macro', 'pdf-acrobat-reader', 'slack-api']

def create_canary_token(
        canaryDomain: str,
        flockID: str,
        factoryAuthToken: str,
        reminder: dict,
        tokenType: str,
        ) -> str | None:

    api_url = f'https://{canaryDomain}.canary.tools/api/v1/canarytoken/factory/create'

    data = {
        'factory_auth': factoryAuthToken,
        'memo': json.dumps(reminder),
        'kind': tokenType,
        'flock_id': flockID,
    }
    print(f'> Creating token: {data}')

    resp = requests.post(api_url, data=data)
    print(f'> RESPONSE: {resp.json()}')

    return resp.json()


def download_canary_token(
        canaryDomain: str,
        factoryAuthToken: str,
        tokenID: str,
        reminder: dict,
        ) -> bytes:
    print(f'> Downloading token: {tokenID}')

    data = {
        'factory_auth': factoryAuthToken,
        'canarytoken': tokenID,
    }

    pathlib.Path(f'tmp').mkdir(parents=True, exist_ok=True)
    
    download_url = f'https://{canaryDomain}.canary.tools/api/v1/canarytoken/factory/download'
    resp = requests.get(download_url, allow_redirects=True, params=data)
    # filename = re.findall("filename=(.+)", resp.headers["Content-Disposition"])[0]
    # filePath = f'tmp/{filename}'
    # with open(filePath, 'wb') as f:
    #     f.write(resp.content)

    # print(f'> Deleting temp file: {filePath}')

    # os.remove(filePath)

    return resp.content



def process_token(row):
    # Make sure that the token path always ends in a '/'
    if len(row['File Path']) > 0 and row['File Path'][-1] != '/':
        row['File Path'] += '/'
    
    reminder = {
        'aws-account-id': row['AWSAccountID'],
        's3-bucket-name': row['S3 Bucket Name'],
        'path': row['File Path'],
        'note': row['Note'],
        'filename': row['Filename'],
        'fullpath': row['File Path'] + row['Filename']
    }

    createResponse = create_canary_token(
        canaryDomain=row['Canary Domain'],
        flockID=row['FlockID'],
        factoryAuthToken=row['FactoryAuthToken'],
        reminder=reminder,
        tokenType=row['Token Type'],
    )

    if createResponse['result'] == 'success':
        fileBytes = download_canary_token(
            canaryDomain=row['Canary Domain'],
            factoryAuthToken=row['FactoryAuthToken'],
            reminder=reminder,
            tokenID=createResponse['canarytoken']['canarytoken']
        )

        upload_to_s3(
            bucket_name=row['S3 Bucket Name'],
            file_bytes=fileBytes,
            file_key=row['File Path'] + row['Filename'],
            profile_name=row['AWS Profile Name']
        )
    else:
        print('> SOMETHING WENT WRONG')

def upload_to_s3(bucket_name, file_bytes, file_key, profile_name):
    try:
        session = boto3.Session(profile_name=profile_name)
        s3 = session.client('s3')
        s3.put_object(Bucket=bucket_name, Key=file_key, Body=file_bytes)

        print(f'File "{file_key}" uploaded successfully using profile "{profile_name}" to bucket "{bucket_name}"')
    except Exception as e:
        print(f'Error uploading file to S3: {e}')

def main(inputFilename: str):
    match inputFilename[-3:]:
        case 'csv':
            delimiter = ','
        case 'tsv':
            delimiter = '\t'
        case _:
            print('Unsupported file type. Please use only one of CSV or TSV')
            exit()

    with open(inputFilename, 'r') as inputFile:
        reader = csv.DictReader(inputFile, delimiter=delimiter)
        for row in reader:
            if row.get('In Scope', 'False').lower() in ['true', 'yes']:
                process_token(row)
            # break

if __name__ == '__main__':
    parser = argparse.ArgumentParser("create_tokens_s3")
    parser.add_argument("--filename", help="A separated value file with all of the information. This can be a CSV or TSV.", type=str, required=True)
    args = parser.parse_args()

    main(args.filename)
