# EnglishPal - Learn English Words Smartly





1 November 2019


## What is it?


EnglishPal allows the user to build his list of new English words
picked from articles selected for him according his vocabulary level.


## Run it on a local machine


`python3 main.py`

Make sure you have the SQLite database file in `app/static` (see below).


## Run it as a Docker container


Assuming that docker has been installed and that you are a sudo user (i.e., sudoer), start the program by typing the following command in directory `EnglishPal`:

`sudo ./build.sh`

Open your favourite Internet browser and enter this URL address: `http://ip-address:90`.

### Explanation on the commands in build.sh

My steps for deploying English on the server.

- ssh to ubuntu@118.*.*.118

- cd to /home/lanhui/englishpal

- Stop all docker service: `sudo service docker restart`.  If you know the docker container ID, then the above command is an overkill.  Use the following command instead: `sudo docker stop ContainerID`.  You could get all container IDs with the following command: `sudo docker ps`

- Rebuild container. Run the following command to rebuild a docker image after the code gets updated: `sudo docker build -t englishpal .`

- Run the application: `sudo docker run -d -p 90:80 -v /home/lanhui/englishpal/app/static/frequency:/app/static/frequency -t englishpal`. If you use `sudo docker run -d -p 90:80 -t englishpal`, data will be lost after terminating the program.

- Save space: `sudo docker system prune -a -f`


### Other useful docker commands

- `sudo docker ps -a`

- `sudo docker logs image_name`, where image_name could be obtained from `sudo docker ps`.

`build.sh` contains all the above commands.  Run "sudo ./build.sh" to rebuild and run the web application.



## Importing articles


All articles are stored in the `article` table in a SQLite file called
`app/static/wordfreqapp.db`.

### Adding new articles

To add articles, open and edit `app/static/wordfreqapp.db` using DB Browser for SQLite (https://sqlitebrowser.org).

### Exporting the database

Export wordfreqapp.db to wordfreqapp.sql using the following commands:

- sqlite3 wordfreqapp.db

- .output wordfreqapp.sql

- .dump

- .exit

Put wordfreqapp.sql (not wordfreqapp.db) under version control.

### Creating SQLite file from wordfreqapp.sql


Create wordfreqapp.db using this command: `cat wordfreqapp.sql |
sqlite3 wordfreqapp.db`.  Delete wordfreqapp.db first if it exists.


### Uploading wordfreqapp.db to the server


`pscp wordfreqapp.db lanhui@118.*.*.118:/home/lanhui/englishpal/app/static`



## Feedback

We welcome feedback on EnglishPal.

### Respondent 1


"Need a phone app.  I use phone a lot.  You cannot ask students to use computers."

Can take a picture for text.  Automatic translation.

### Respondent 2


????????????????????????????????????

??????????????????????????????

????????????????????????????????????????????????

?????????????????????????????????

??????????????????????????????????????????






