yes | docker container prune
docker run --name stem --env-file ../.env -p 9000:8080 stem-container:latest