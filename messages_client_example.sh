#!/bin/bash
api="https://l7kjk6dx49.execute-api.us-east-1.amazonaws.com/prod/postedmessage"
secret="T60pTVm6XjUwCjjyQ9nH"
userid="amzn1.ask.account.AGLZF5TKU7KSKR6KTX6VZXZFA4OJJFVJNMEZZXBFWXOR355IWHR7EIZV4MGJKRLLCX7FMM6KSQYV5KAB4RPO6WOICVFDIRSP7PZFXGWY7GJMNWOGF5ALRMMTMIL3IJW3GQBABTSFIC4P5RYFQIJ2NKTGVLAY72YIGIQVMG6BTDYQF443FL6TEEX5GZRXCDOOD6VIZPOK7ZW3AQI"
temp=$(/usr/local/bin/temper-poll | tail -n 1 | cut -c 12-15)
timestamp=$(date +%s)
sticky=$(($timestamp + 3600))
hash=$(echo -n $timestamp':'$secret | md5sum | cut -c 1-32)
curl -s $api -H 'Content-Type: application/json; charset=UTF-8' --data-binary '{"key":"temper-downstairs","text":"The temperature downstairs is '"$temp"'","userId":"'"$userid"'","timestamp":'"$timestamp"',"hash":"'"$hash"'","source":"api","sticky":"'"$sticky"'"}' > /dev/null