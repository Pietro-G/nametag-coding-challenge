# Variables
PYTHON = python
PIP = pip
REQUIREMENTS_FILE = requirements.txt
EXE_NAME = main
SCRIPT = client/main.py
BUILD_DIR = client/build
DIST_DIR = client/dist
SPEC_FILE = client/$(EXE_NAME).spec
EXE_PATH = $(DIST_DIR)/$(EXE_NAME)

# Default target
all: install build

# Install requirements/dependencies
install:
	$(PIP) install -r $(REQUIREMENTS_FILE)

# Build the executable using PyInstaller inside the client directory
build: install
	cd client && $(PYTHON) -m PyInstaller --onefile --windowed $(notdir $(SCRIPT)) && \
	mkdir -p $(DIST_DIR) && \
	find . -maxdepth 1 -mindepth 1 ! -name build ! -name dist -exec cp -r {} $(DIST_DIR) \;

# Clean build artifacts
clean:
	rm -rf $(BUILD_DIR) $(DIST_DIR) $(SPEC_FILE)

# Run the executable
run:
	$(EXE_PATH)

.PHONY: all install build clean run
