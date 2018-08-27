EXPORT_DIR="export"
PYTHON=pypy

web:
				find ./src -name "*.py" -o -name "*.html" -o -name "*.css" | entr -r ${PYTHON} src/web.py

clean:
				rm ./db/wiki.sqlite3
				${PYTHON} src/models.py

ingest: cleanfiles
				${PYTHON} src/ingest_flat_files.py -y config/local.yaml

exgest:
				rm -fr ${EXPORT_DIR}/* || true
				mkdir ${EXPORT_DIR} || true
				(cd ${EXPORT_DIR} && git init .) || true
				${PYTHON} src/exgest_flat_files.py -d ${EXPORT_DIR}
				cd ${EXPORT_DIR} && git add . && git commit -a -v -m "[autocommit] `date '+%Y-%m-%d %H%M'`"

cleanfiles:
				pypy src/clean_missing_files.py
