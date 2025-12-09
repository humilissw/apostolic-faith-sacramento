# Docker

## Brief Primer

Docker is a **containerization** engine that allows you to run applications in very tiny, trimmed down virtual machines called **containers**.  

### What is a container?

A container is like a Virtual Machine, but:

1. It doesn't have a graphical user interface
2. It has a bare-bones kernel, which is typically MB large.
3. It **shares** the physical architecture of the host, unlike a VM.  
   1. You can also run a container against a different CPU architecture, as well.
   2. VMs "fake," or simulate the physical architecture
4. It requires a "blueprint" to be setup in the form of a **Dockerfile**.
   1. Here you can specify additional things to be added to the container OS, such as **bash**, or some other CLI tooling that you need in your container startup process.
5. Is incredibly versatile in isolating your environment from your local machine
   1. "It works on my machine" is a thing of the past.
   2. You can build a container and have it run anywhere containers are supported, if done properly.

### How do I use them?

Applications that use containers are so-called **containerized applications**. These applications can be fully-built, working, off-the-shelf applications with minimal effort in getting them to work on your machine.

You typically work with containers in a process as follows:

1. Create a blueprint file for your container, i.e., a **Dockerfile**.
2. Build the image for your container locally in the container engine, such as **Docker**, or **Podman**.
   1. Typically you will also **tag** your container with a specific version, or **latest** to specify that this container is the **latest version**.
3. Run the container, specifying the ports, environment variables, and any other resources the container will need. So:
   1. Ports
   2. Volumes
   3. Networks
   4. Dependencies
   5. Environment Variables
4. Access the container at the specified ports that were mapped from the container OS to the host OS.
   1.  If the container's application port is :443, you can map the same port to the OS's port, :443, but you ideally should map it to another port, especially for common ports such as :80 and :443.  
       1.  These are commonly used by webservers, so if you are hosting a web server, that would likely be a valid use-case.
       2.  Example: 
           1.  `- 5000:443` (docker-compose)
           2.  `-p 5000:443`
   
### Docker-Compose

Docker-Compose is Docker's way of building a **microservices cluster**.  You use docker-compose to stand up a cluster of containers and work with those containers as you see fit.

This is incredibly powerful because if you are building an application, you can standup an entire cluster of technical dependencies, such as:

- Caching
- Database
- Message Queue/Bus
- Authorization Services, such as a Secure Token Service (STS)
- Metrics tooling, such as **Prometheus**
- Service Discovery, such as **Hashicorp Consul**
- Web Server, such as **Nginx**
- Application Specific images, such as **nodejs**, **dotnet**, **java**, **python**, and many others.

## Key points for working with Docker

- Building images requires you to have an **image blueprint file** to work with, such as a **Dockerfile**. 
- You must understand how docker context works.  If you run a build command at the root of your project, for example, and the Dockerfile is somewhere in your root, all of the references within your Dockerfile must be correctly set for your specific image; otherwise, you will have a lot of issues.
- In this repository, if you want to run the cluster associated with the database, you need to switch directories to where the file lives; otherwise, you have to specify the folder like so:

```bash
docker-compose -f ./db/compose.db.yml up -d --build
```

- **Docker is not easy.** Understanding how everything works involves understanding a lot about Docker.  However, as they say, **with great risk comes great rewards.**. Learn Docker and you will be a hugely valuable resource!







