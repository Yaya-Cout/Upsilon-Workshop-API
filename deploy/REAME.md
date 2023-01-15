# Deploy guide

This guide is not complete yet, it is more notes than a real documentation.

## Build the docker image

If you want to build you own image, you need to build it using this command:

```shell
docker build -t workshop .
```

## Test the docker image locally

To test the docker image locally, you can run the following command:

```shell
docker run -itp 80:80 workshop
```

You can use this variant to run the container in the background:

```shell
docker run -itp 80:80 workshop
```

## Sign in to Docker Hub (only the first time if you want to push the image)

```shell
docker login
```

## Create repository in Docker Hub

Go to [Docker Hub](https://hub.docker.com/) and create a new repository named
`upsilon-workshop` in the `Repositories` section.

## Tag the image

```shell
docker tag workshop <your-docker-hub-username>/upsilon-workshop
```

## Push the image to Docker Hub

```shell
docker push <your-docker-hub-username>/upsilon-workshop
```
