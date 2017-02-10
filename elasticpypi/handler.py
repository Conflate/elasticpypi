import re
import boto3
from elasticpypi.name import compute_package_name, normalize
from elasticpypi.config import config

TABLE = config['table']


def s3(event, context):
    filename = event.get('Records')[0]['s3']['object']['key']
    package_name = compute_package_name(filename)
    version = get_version(filename)
    normalized_name = normalize(package_name)
    if 'Delete' in event['Records'][0]['eventName']:
        delete_item(package_name, version)
        return None
    put_item(package_name, version, filename, normalized_name)
    return None


def get_version(key):
    match = re.match('.+-(?P<version>.*)\.tar\.gz$', key)
    if match:
        return match.group('version')
    return key


def delete_item(package_name, version):
    print('delete', package_name, version)
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(TABLE)
    table.delete_item(Key={
        'package_name': package_name,
        'version': version,
    })


def put_item(package_name, version, filename, normalized_name):
    print('put', package_name, version, filename, normalized_name)
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(TABLE)
    table.put_item(
        Item={
            'package_name': package_name,
            'version': version,
            'filename': filename,
            'normalized_name': normalized_name,
        }
    )
