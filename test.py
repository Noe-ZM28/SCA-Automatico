import redis
import datetime

creds_provider = redis.UsernamePasswordCredentialProvider("default", "3162emmr5E0aEwPCNe8SiqmBnlEpsGsl")
r = redis.Redis(host="redis-15130.c61.us-east-1-3.ec2.redns.redis-cloud.com", port=15130, credential_provider=creds_provider)

print(r.ping())


stream_key = "skey"
group1 = "grp1"
group2 = "grp2"

for i in range(0,10):
    r.xadd( stream_key, { 'ts': str(datetime.datetime.now()), 'v': i } )
print( f"stream length: {r.xlen( stream_key )}")



l = r.xread( count=2, streams={stream_key} )
first_stream = l[0]
print( f"got data from stream: {first_stream[0]}")
fs_data = first_stream[1]
for id, value in fs_data:
    print( f"id: {id} value: {value[b'v']}")