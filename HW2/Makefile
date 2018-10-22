PYTHON = python
VIEWER = more
CLIENT = client.py
SUDO = sudo
PYDOC = pydoc client logging
ARGS = 10.246.251.93 client.log

.PHONY: run view clean

run:
	$(PYTHON) $(CLIENT) $(ARGS)
view:
	$(VIEWER) $(CLIENT) $(SERVER) README
client:
	$(PYTHON) $(CLIENT) $(ARGS)
docs:
	$(PYDOC)
clean:
	@echo "Removing .pyc and log files"
	@rm *.pyc
