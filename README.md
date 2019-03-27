# CS472

### HW1 : Computer Network Problems

### HW2 : FTP Client

```
Files:
client.py
logging.py
sample-client.log

Makefile Commands:
run: run program on drexel ftp server
	<python client.py 10.246.251.93 client.log>
view:
	view source files
docs:
	view pydoc documentation of source files
clean:
	removes pyc and logfile


CLI commands:
user quit pasv
epsv port cd
eprt retr stor
syst ls pwd
help pass
```

### HW3 : FTP Server

```
Makefile commands:
	run: runs server on port 2121
	view: view the server source code
	docs: view pydocs comments
	test: run simple ftp test using the ftp client
	clean: remove pyc files


Running: 
	You can use the makefile to run this command or run it manaully
	python server.py <log file> <port>

Files:
	server.py : main FTP server
	logging.pg : logger class
	Makefile :	makefile to run program
	sample-server.log : sample server log
	sample-client.log : sample ftp client interaction with server
	users.ini : user config file
	tests/test.sh : sample test script to run with ftp server
	HW3-DFA.png : the DFA image
```

### HW4 : SFTP 

```
Makefile commands:
	run: runs server on port 2121
	view: view the server source code
	docs: view pydocs comments
	clean: remove pyc files

Running:
	You can use the makefile to run this command or run it manually
	python server.py <log file> <port>

Development Info:
	python2.7
	Requirements maybe configparser already installed on tux (used to parse config file):
		pip install configparser==3.5.0

Files:
	server.py : main FTP server
	logging.pg : logger class
	Makefile : makefile to run program
	config.ini : config file for server settings and authorized users
	server.key : generated server key for SSL implicit mode
	server.crt : generated server certificate for SSL implicit mode
	sample-client.log : sample client log of passing requirements
	sameple-server.log : sample server log of those requests


Config File {config.ini}
	[FTP Server Config]
	port_mode : yes ;disable port mode
	pasv_mode : no ;disable passive mode
	ftps_mode : no ;enable implicit mode
  ```
