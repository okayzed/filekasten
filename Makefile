web:
				ls src/*.py | entr -r python src/web.py

clean:
				rm ./db/wiki.sqlite3
				python src/models.py

ingest:
				python src/ingest_flat_files.py -y config/local.yaml



make exgest:
				rm -fr export/ || true
				python src/exgest_flat_files.py -d export/
