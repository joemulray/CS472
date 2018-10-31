PYTHON = python
VIEWER = more
SERVER = server.py
SUDO = sudo
PYDOC = pydoc server logging
ARGS = server.log 2121

.PHONY: run view clean

run:
	$(PYTHON) $(SERVER) $(ARGS)
view:
	$(VIEWER) $(SERVER) $(SERVER) README
server:
	$(PYTHON) $(SERVER) $(ARGS)
docs:
	$(PYDOC)
clean:
	@echo "Removing .pyc and log files"
	@rm *.pyc
