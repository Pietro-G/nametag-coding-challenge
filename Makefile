# Paths
SCRIPT = client/client.py
ASSETS_DIR = client/assets
DIST_DIR = client/dist
BUILD_DIR = client/build
VERSION_FILE = client/version.txt

all: install build

install:
	pip install -r requirements.txt

build: install
	python -m PyInstaller --onefile --windowed \
		--add-data "$(ASSETS_DIR):assets" \
		--add-data "$(VERSION_FILE):." \
		--distpath $(DIST_DIR) \
		--workpath $(BUILD_DIR) \
		$(SCRIPT)

clean:
	rm -rf $(BUILD_DIR) $(DIST_DIR) client/*.spec

run-client:
	$(DIST_DIR)/client

run-server:
	python server/server.py

.PHONY: all install build clean run
