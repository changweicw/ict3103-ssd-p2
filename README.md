# ict3x03-ssd-p2
Welcome to our humble e-commerce store, the Collaboratory Mall. Where we sell _**real**_-looking products.

## Docker Building instructions
**On your host:**
1. docker build -t <docker_username>/<anyName>:<Tag/Branch>
1. docker push <docker_username>/<anyName>:<Tag/Branch>

**On the server:**
1. docker pull <docker_username>/<anyName>:<Tag/Branch>
1. docker run -d -p 5000:5000 <docker_username>/<anyName>:<Tag/Branch>


### **EXAMPLE**

**On your host:**

`docker build -t raphaelchia/collabMall:v1.0`

`docker push raphaelchia/collabMall:v1.0`

**On the server:**

`docker pull raphaelchia/collabMall:v1.0`

`docker run -d -p 5000:5000 raphaelchia/collabMall:v1.0`

### Useful Docker CLI commands
` docker images`

Shows all images on your host

` docker ps `

Shows Current running image

`docker system prune -a`

Purging All Unused or Dangling Images, Containers, Volumes, and Networks
