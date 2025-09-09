echo " Cleaning up Docker containers and images..."

docker ps -a --filter "name=cicd-simulator-container" --format "{{.ID}}" | xargs -r docker rm -f
docker ps -a --filter "name=cicd-base-container" --format "{{.ID}}" | xargs -r docker rm -f

docker images "cicd-simulator*" -q | xargs -r docker rmi -f
docker images "cicd-base*" -q | xargs -r docker rmi -f


docker system prune -f

echo "Cleanup complete."
