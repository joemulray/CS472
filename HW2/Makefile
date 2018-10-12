PYTHON = python
VIEWER = more
CLIENT = client.py
SERVER = server.py
SUDO = sudo

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

clean:
	@echo "Removing .pyc and log files"
	@rm *.pyc
	@rm *.log
