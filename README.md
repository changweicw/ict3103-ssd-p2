# ict3x03-ssd-p2
Welcome to our humble e-commerce store, the Collaboratory Mall. Where we sell _**real**_-looking products.

## Project Running Instructions
Ensure you got your python virtual env set up.
Python 3.8.5 will not work. Recommended python 3.8.
Do in order 
1. ` pip install virtualenv `
1. ` virtualenv --version ` To ensure you already installed it properly.
Now go to your project folder and run
1. ` virtualenv env `
1. Ask for the bucket-key.json and .env from the people you know. If you dont know who to ask from, you are not supposed to run this project.
1. Put the both files in the root of this python app
1. ` pip install -r requirements.txt `
1. ` python main.py `


## Docker Building instructions
**PRE-REQUISITE**
1. Check your .Dockerignore file and ensure **/.env file is not inside there.
1. Ensure that server is = prod in main.py file before building the docker.
1. Lastly ensure that your .env email_templates folder is using a forward slash because linux.
1. Check your .env folder serverip and serverport are correct. (collaboratory.sitict.net,3389)

**On your host:**
1. docker build -t <docker_username>/<anyName>:<Tag/Branch>
1. docker push <docker_username>/<anyName>:<Tag/Branch>

**On the server:**
1. docker pull <docker_username>/<anyName>:<Tag/Branch>
1. docker run -d -p 5000:5000 <docker_username>/<anyName>:<Tag/Branch>


### **EXAMPLE**

**On your host:**

`docker build -t raphaelchia/collabMall:v1.0 .` (Note the fullstop at the end)

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
