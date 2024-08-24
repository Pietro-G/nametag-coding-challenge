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
	$(DIST_DIR)/client$(EXE_SUFFIX)

run-server:
	python server/server.py

update:
	@echo "Detecting OS..."
	@UNAME_S=$(shell uname -s) && \
	if [ "$$UNAME_S" = "Linux" ]; then \
		python updater.py || { echo "Update failed or no update available"; exit 0; }; \
	elif [ "$$UNAME_S" = "Darwin" ]; then \
		python updater.py || { echo "Update failed or no update available"; exit 0; }; \
	elif [ "$$UNAME_S" = "CYGWIN_NT-10.0" ]; then \
		python updater.py || { echo "Update failed or no update available"; exit 0; }; \
	else \
		echo "Unsupported OS"; \
		exit 1; \
	fi

.PHONY: all install build clean run-client run-server update
