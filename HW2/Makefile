PYTHON = python
VIEWER = more
CLIENT = client.py
SERVER = server.py

.PHONY: run view clean

run:
	$(PYTHON) $(CLIENT)
	$(PYTHON) $(SERVER)
view:
	$(VIEWER) $(CLIENT) $(SERVER) README

clean:
	@rm *.pyc

