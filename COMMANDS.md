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

#### /evaluation GET (list all evaluations)

curl -X GET http://127.0.0.1:7000/evaluation

#### /evaluation/{id} GET (get status of a specific evaluation)

# Replace {id} with an actual evaluation ID
curl -X GET http://127.0.0.1:7000/evaluation/{id}
