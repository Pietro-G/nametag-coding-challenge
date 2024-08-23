# Paths
SCRIPT = client/client.py
BUILD_DIR = client/build
DIST_DIR = client/dist
SPEC_FILE = client/$(EXE_NAME).spec
EXE_PATH = $(DIST_DIR)/$(EXE_NAME)

all: install build

install:
	pip install -r requirements.txt

build: install
	cd client && $(PYTHON) -m PyInstaller --onefile --windowed $(notdir $(SCRIPT)) && \
	mkdir -p $(DIST_DIR) && \
	find . -maxdepth 1 -mindepth 1 ! -name build ! -name dist -exec cp -r {} $(DIST_DIR) \;

clean:
	rm -rf $(BUILD_DIR) $(DIST_DIR) $(SPEC_FILE)

run-client:
	python client/client.py

run-server:
	python server/server.py

.PHONY: all install build clean run
