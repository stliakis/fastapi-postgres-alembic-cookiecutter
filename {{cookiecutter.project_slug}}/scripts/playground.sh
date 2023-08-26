#! /usr/bin/env bash
echo "------------Running playground.py-------------"
docker-compose exec backend python /app/app/scripts/playground.py;
echo "------------Finished running playground.py-------------"
echo "waiting for change..."
while inotifywait --quiet -e close_write backend/app/app/scripts/playground.py;
do
  echo "------------Running playground.py-------------"
  docker-compose exec backend python /app/app/scripts/playground.py;
  echo "------------Finished running playground.py-------------"
  echo "waiting for change..."
done

