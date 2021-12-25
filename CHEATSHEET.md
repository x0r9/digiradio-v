# Cheatsheet

## Start Direwolf
`direwolf`

## Start aprsdump
`cd src`
`source  venv/bin/activate`
`python aprsdump.py -out file-dump.txt`

## Start Redis 
`sudo docker run --name some-redis -p 6379:6379 --rm -d redis`

### stop redis (for reload?)
`sudo docker stop some-redis`

## Start Redis Feeder
`cd src`
`source  venv/bin/activate`
`python redis_feeder.py -file file-dump.txt`

## Start Web App (dev)
`cd src`
`source  venv/bin/activate`
`uvicorn fast-demo:app --port 8080  --reload`
