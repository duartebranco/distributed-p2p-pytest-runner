## API

#### /evaluation POST GIT (should return id)

curl -X POST http://127.0.0.1:7000/evaluation \
 -H 'Content-Type: application/json' \
 -d '{
    "auth_token":"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",
    "projects":[
        "https://github.com/detiuaveiro/cd2025_guiao1-duartebranco",
        "https://github.com/detiuaveiro/cd2025_chord-120603_119253",
        "https://github.com/detiuaveiro/cd2025-guiao-3-120603_119253",
        "https://github.com/detiuaveiro/cd2025-guiao-4-120603_119253"
    ]
 }'

#### /evaluation POST ZIP (should return id)

curl -X POST http://127.0.0.1:7000/evaluation \
 -H 'Content-Type: multipart/form-data' \
 -F "file=@/home/duarte/all_projects.zip"

#### /evaluation GET (list all evaluations) ***(not completely right)

curl -X GET http://127.0.0.1:7000/evaluation

#### /evaluation/{id} GET (get status of a specific evaluation)

curl -X GET http://127.0.0.1:7000/evaluation/{id}

#### /stats GET



#### /network GET



## NODE

#### add
curl -X POST http://localhost:7000/network \
     -H "Content-Type: application/json" \
     -d '{"address":"192.168.1.100:7001"}'

#### list
curl http://localhost:7000/network

#### delete
curl -X DELETE http://localhost:7000/network \
     -H "Content-Type: application/json" \
     -d '{"address":"192.168.1.100:7001"}'