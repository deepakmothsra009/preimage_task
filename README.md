# preimage_task

Functionality:

1. The service lets its users create a project with N number of images and generates something [a list of files] (a 3D model using those images).
2. Users can then later on add/remove more images to that project and the model will be recomputed again with the new set of images.
3. The system will store all the images, history and all versions of the model so that users can compare the difference later on between different versions.
4. The service is also responsible for making those models available to the user (consumers) later on.

Components:::
Storage: local storage
Messaging Broker: Rabbitmq
Database: Postgresql

Services:::
Ingestor:
The role of the ingestor is to download/modify given images for a project and store it in the storage
and create relevant entries in the database.
In case the user wants to add/remove images from an existing project,
Ingestor should handle that too by adding/removing images from that project

Enricher:
returns images list of the version to consumer

Consumer:
it maintains a list of subscribers in the database. Whenever a new version of the model is available it sends that information to all the subscribers who have subscribed to the updates of that particular project.
You can use the same messaging system here as well. One topic per project.

Project Setup:
git clone <link to this repo>
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

db table info::
user_info_table:
user_id SERIAL PRIMARY KEY
user_name TEXT

project_info_table:
project_id SERIAL PRIMARY KEY
user_id INTEGER REFERENCES user_info_table,
project_name TEXT

project_version_table:
project_version_id SERIAL PRIMARY KEY
project_id INTEGER REFERENCES project_info_table
project_version_name TEXT
project_version_number INTEGER
row_insert_time TIMESTAMP DEFAULT NOW(),
UNIQUE (project_id,project_version_id, project_version_name)

project_version_result_table:
version_result_id SERIAL PRIMARY KEY
project_version_id INTEGER REFERENCES project_version_table
project_version_result_path TEXT
