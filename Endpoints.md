## API

#### /evaluation POST GIT (should return id)

curl -X POST http://192.168.0.2:7000/evaluation \
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

curl -X POST http://192.168.0.2:7000/evaluation \
 -H 'Content-Type: application/json' \
 -d '{
    "auth_token":"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",
    "projects":[
        "https://github.com/detiuaveiro/cd2025_guiao1-duartebranco"
    ]
 }'

curl -X POST http://192.168.0.2:7000/evaluation \
 -H 'Content-Type: application/json' \
 -d '{
    "auth_token":"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",
    "projects":[
        "https://github.com/detiuaveiro/cd2025_chord-120603_119253"
    ]
 }'

curl -X POST http://192.168.0.2:7000/evaluation \
 -H 'Content-Type: application/json' \
 -d '{
    "auth_token":"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",
    "projects":[
        "https://github.com/detiuaveiro/cd2025-guiao-3-120603_119253"
    ]
 }'

curl -X POST http://192.168.0.2:7000/evaluation \
 -H 'Content-Type: application/json' \
 -d '{
    "auth_token":"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",
    "projects":[
        "https://github.com/detiuaveiro/cd2025-guiao-4-120603_119253"
    ]
 }'

#### /evaluation POST ZIP (should return id) (not done yet)

curl -X POST http://192.168.0.2:7000/evaluation \
 -H 'Content-Type: multipart/form-data' \
 -F "file=@/home/duarte/Transferências/projects.zip"

#### /evaluation GET (list all evaluations)

curl -X GET http://192.168.0.2:7000/evaluation

#### /evaluation/{id} GET (get status of a specific evaluation)

curl -X GET http://192.168.0.2:7000/evaluation/{id}

#### /stats GET (not done yet)

curl -X GET http://192.168.0.2:7000/stats

#### /network GET (p2p network info)

curl -X GET http://192.168.0.2:7000/network

for i in {1..3}; do docker-compose logs node$i > node${i}_logs.txt; done
