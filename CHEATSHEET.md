# Cheatsheet

## Start Direwolf
``

## Start aprsdump
`cd src`
`source  venv/bin/activate`
`python aprsdump.py -out file-dump.txt`

## Start Redis 
``sudo docker run --name some-redis -p 6379:6379 --rm -d redis

## Start Redis Feeder
`cd src`
`source  venv/bin/activate`
`python redis_feeder.py -file file-dump.txt`
