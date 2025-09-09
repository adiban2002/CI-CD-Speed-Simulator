echo "Starting CI/CD Speed Simulator..."

if command -v docker compose &> /dev/null; then
  docker compose -f docker/docker-compose.yml run --rm simulator
else
  docker-compose -f docker/docker-compose.yml run --rm simulator
fi
