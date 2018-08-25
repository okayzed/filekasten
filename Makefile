web:
				ls src/*.py | entr -r python src/web.py

clean:
				rm ./db/wiki.sqlite3
				python src/models.py

ingest:
				python src/ingest_flat_files.py -d ~/Notes/
				python src/ingest_flat_files.py -d ~/Sync/notes/
				python src/ingest_flat_files.py -d ~/Sync/quotes/ -n rambles
				python src/ingest_flat_files.py -d ~/Sync/plans/ -n plans
				python src/ingest_flat_files.py -d ~/.local/share/sjrn/ -n sjrn
				python src/ingest_flat_files.py -d ~/tonka/src/idealogue/site/_ideas/ -n ideas
				python src/ingest_flat_files.py -d ~/tonka/src/logv.github.io/_posts/ -n logv_site
				python src/ingest_flat_files.py -d ~/tonka/src/phisicist/_posts/ -n phil/pub



make exgest:
				rm -fr export/ || true
				python src/exgest_flat_files.py -d export/
