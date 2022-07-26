# preimage_task

To setup Rabbitmq and postgres containers:
cd preimage_task/docker
docker-compose up &

To setup preimage_container (which has ingestor, enricher, consumer services)
cd preimage_task
sudo docker build -f docker/Dockerfile . -t preimage_task:v1
sudo docker run --detach --mount 'type=bind,src=/home/deepak/data,dst=/data' --add-host=host.docker.internal:host-gateway --env-file docker/docker.env --name preimage_container.v1 -d preimage_task:v1

To push images for a project (from outside the container)
python3 image_pusher.py <user_name> <project_name>

To subscribe to a project (from outside the container)
python3 external_consumer.py <project_name>

#sudo docker exec -it preimage_container.v1 /bin/bash
