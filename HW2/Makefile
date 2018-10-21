PYTHON = python
VIEWER = more
CLIENT = client.py
SERVER = server.py
SUDO = sudo
PYDOC = pydoc client
ARGS = 127.0.0.1 client.log 2121

.PHONY: run view clean

run:
	$(PYTHON) $(CLIENT) $(ARGS)
view:
	$(VIEWER) $(CLIENT) $(SERVER) README

client:
	$(PYTHON) $(CLIENT) $(ARGS)

server:
	$(SUDO) $(PYTHON) $(SERVER)

docs:
	$(PYDOC)

clean:
	@echo "Removing .pyc and log files"
	@rm *.pyc
	@rm *.log
