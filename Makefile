EXPORT_DIR="export"

web:
				ls src/*.py | entr -r python src/web.py

clean:
				rm ./db/wiki.sqlite3
				python src/models.py

ingest:
				python src/ingest_flat_files.py -y config/local.yaml

make exgest:
				rm -fr ${EXPORT_DIR}/* || true
				mkdir ${EXPORT_DIR} || true
				(cd ${EXPORT_DIR} && git init .) || true
				python src/exgest_flat_files.py -d ${EXPORT_DIR}
				cd ${EXPORT_DIR} && git add . && git commit -a -v -m "[autocommit] `date +%Y-%m-%d %H%M`"
