## Developing using Docker

* Have docker installed
* clone this repo and navigate to this directory
* run `docker build . --tag khbr`
* run `docker run -it -v %cd%/src:/app/src -v %cd%/public:/app/public -p 3001:3000 -e CHOKIDAR_USEPOLLING=true khbr:latest`

* After a minute the console will say it was compiled successfully and the site will be available at `localhost:3001` (and your changes will hot reload). Closing the terminal will cause the server to shut down.