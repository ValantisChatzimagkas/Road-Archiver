# Task - Development of REST API for management of road networks
The task is made up of three subtasks, all of which must be completed. The aim is to create a simple Rest API for managing road networks. Three example road networks (node-edge models) in GeoJSON format are attached for processing the task.


## Tasks:
### Task 1

The first two road networks should be uploaded via an endpoint and stored in a PostgreSQL database. Since the road networks essentially consist of geometries, the use of a geo-extension such as PostGIS is recommended in order to store the data efficiently. As the road networks belong to different customers, they must have a corresponding attribute to enable simple authorization.

### Task 2

The third road network is an updated version of the second network. It should be possible to perform an update via another endpoint by uploading the updated version of the network. During an update, the original edges should not be deleted, but only marked as not up-to-date.

### Task 3

The edges of the road networks should be retrievable via an additional endpoint in GeoJSON format. The endpoint should only return the edges of the specified network of an authenticated customer. It should also be possible to use a parameter to specify which point in time the network should correspond to, i.e. network 2 should be able to be retrieved in its state before and after the update.


## Specifications


1. The API framework to be used should be Flask or FastAPI, while the database is to be realized using Postgres.
2. A README.md should document the application and the approach to the task.
3. The solution must be containerized and readily executable using Docker-Compose.


