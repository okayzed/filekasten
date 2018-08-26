EXPORT_DIR="export"
PYTHON=python

web:
				find ./src -name "*.py" -o -name "*.html" -o -name "*.css" | entr -r ${PYTHON} src/web.py

clean:
				rm ./db/wiki.sqlite3
				${PYTHON} src/models.py

ingest:
				${PYTHON} src/ingest_flat_files.py -y config/local.yaml 2>&1 > ~/.jotiki.err

make exgest:
				rm -fr ${EXPORT_DIR}/* || true
				mkdir ${EXPORT_DIR} || true
				(cd ${EXPORT_DIR} && git init .) || true
				${PYTHON} src/exgest_flat_files.py -d ${EXPORT_DIR}
				cd ${EXPORT_DIR} && git add . && git commit -a -v -m "[autocommit] `date '+%Y-%m-%d %H%M'`"
