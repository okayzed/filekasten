EXPORT_DIR="export"
PYTHON=python

web:
				find ./filekasten -name "*.py" -o -name "*.html" -o -name "*.css" | entr -r ${PYTHON} filekasten/web.py

clean:
				rm ./db/wiki.sqlite3
				${PYTHON} filekasten/models.py

ingest: cleanfiles
				${PYTHON} filekasten/ingest_flat_files.py -y config/local.yaml

exgest:
				rm -fr ${EXPORT_DIR}/* || true
				mkdir ${EXPORT_DIR} || true
				${PYTHON} filekasten/exgest_flat_files.py -d ${EXPORT_DIR}

cleanfiles:
				${PYTHON} filekasten/clean_missing_files.py

.PHONY: build

build:
				${PYTHON} setup.py sdist

install:
				sudo ${PYTHON} -m pip install dist/filekasten-0.0.1.tar.gz --upgrade
