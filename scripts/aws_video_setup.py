# coding: utf-8
"""Create S3 bucket + CloudFront distribution (OAC) for campaign videos, upload all.
Idempotent/resumable: skips existing bucket, distribution, and already-uploaded files."""
import io, json, mimetypes, sys
from pathlib import Path
import boto3

REGION = 'eu-west-1'
BUCKET = 'lydraedisveislan-videos'
ROOT = Path(__file__).parent.parent
MEDIA = ROOT / 'esb-videos' / 'media'

s3 = boto3.client('s3', region_name=REGION)
cf = boto3.client('cloudfront')

# 1. Bucket
try:
    s3.head_bucket(Bucket=BUCKET)
    print('bucket exists', flush=True)
except Exception:
    s3.create_bucket(Bucket=BUCKET, CreateBucketConfiguration={'LocationConstraint': REGION})
    print('bucket created', flush=True)

# 2. Upload (skip already-present by size)
existing = {}
paginator = s3.get_paginator('list_objects_v2')
for page in paginator.paginate(Bucket=BUCKET, Prefix='media/'):
    for o in page.get('Contents', []):
        existing[o['Key']] = o['Size']

files = sorted(MEDIA.glob('*.mp4'))
up = skip = 0
for f in files:
    key = 'media/' + f.name
    if existing.get(key) == f.stat().st_size:
        skip += 1
        continue
    s3.upload_file(str(f), BUCKET, key, ExtraArgs={
        'ContentType': 'video/mp4',
        'CacheControl': 'public, max-age=31536000, immutable',
    })
    up += 1
    if up % 20 == 0:
        print(f'{up} uploaded', flush=True)
print(f'upload done: {up} new, {skip} skipped', flush=True)

# 3. Origin Access Control
oac_id = None
for o in cf.list_origin_access_controls().get('OriginAccessControlList', {}).get('Items', []):
    if o['Name'] == 'lydraedisveislan-videos-oac':
        oac_id = o['Id']
if not oac_id:
    oac_id = cf.create_origin_access_control(OriginAccessControlConfig={
        'Name': 'lydraedisveislan-videos-oac', 'SigningProtocol': 'sigv4',
        'SigningBehavior': 'always', 'OriginAccessControlOriginType': 's3',
    })['OriginAccessControl']['Id']
print('oac:', oac_id, flush=True)

# 4. Distribution
dist = None
for d in cf.list_distributions().get('DistributionList', {}).get('Items', []) or []:
    if d.get('Comment') == 'lydraedisveislan campaign videos':
        dist = d
if not dist:
    origin_domain = f'{BUCKET}.s3.{REGION}.amazonaws.com'
    r = cf.create_distribution(DistributionConfig={
        'CallerReference': 'lydraedisveislan-videos-1',
        'Comment': 'lydraedisveislan campaign videos',
        'Enabled': True,
        'DefaultCacheBehavior': {
            'TargetOriginId': 's3-videos',
            'ViewerProtocolPolicy': 'redirect-to-https',
            'AllowedMethods': {'Quantity': 2, 'Items': ['GET', 'HEAD'],
                               'CachedMethods': {'Quantity': 2, 'Items': ['GET', 'HEAD']}},
            'Compress': False,
            'CachePolicyId': '658327ea-f89d-4fab-a63d-7e88639e58f6',
        },
        'Origins': {'Quantity': 1, 'Items': [{
            'Id': 's3-videos', 'DomainName': origin_domain,
            'OriginAccessControlId': oac_id,
            'S3OriginConfig': {'OriginAccessIdentity': ''},
        }]},
        'PriceClass': 'PriceClass_100',
        'HttpVersion': 'http2and3',
    })
    dist = r['Distribution']
    dist_id, domain = dist['Id'], dist['DomainName']
else:
    dist_id, domain = dist['Id'], dist['DomainName']
print('distribution:', dist_id, domain, flush=True)

# 5. Bucket policy: allow this distribution via OAC
account = boto3.client('sts').get_caller_identity()['Account']
policy = {
    'Version': '2012-10-17',
    'Statement': [{
        'Sid': 'AllowCloudFrontOAC', 'Effect': 'Allow',
        'Principal': {'Service': 'cloudfront.amazonaws.com'},
        'Action': 's3:GetObject', 'Resource': f'arn:aws:s3:::{BUCKET}/*',
        'Condition': {'StringEquals': {'AWS:SourceArn': f'arn:aws:cloudfront::{account}:distribution/{dist_id}'}},
    }],
}
s3.put_bucket_policy(Bucket=BUCKET, Policy=json.dumps(policy))
print('bucket policy set', flush=True)
json.dump({'bucket': BUCKET, 'distribution': dist_id, 'domain': domain},
          io.open(ROOT / 'scripts' / 'aws_video_cdn.json', 'w', encoding='utf-8'), indent=1)
print(f'CDN READY: https://{domain}/media/', flush=True)
