PYTHON = python
VIEWER = more
CLIENT = client.py
SERVER = server.py
SUDO = sudo
PYDOC = pydoc client

.PHONY: run view clean

run:
	$(PYTHON) $(CLIENT)
	$(PYTHON) $(SERVER)
view:
	$(VIEWER) $(CLIENT) $(SERVER) README

client:
	$(PYTHON) $(CLIENT)

server:
	$(SUDO) $(PYTHON) $(SERVER)

docs:
	$(PYDOC)

clean:
	@echo "Removing .pyc and log files"
	@rm *.pyc
	@rm *.log
