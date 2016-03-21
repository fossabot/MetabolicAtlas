.PHONY: all clean test

all:
	python runserver.py

clean:
	rm -f hma_backend/test-db.sqlite
	rm -f */*.pyc
	rm -rf tmp
	rm -rf __pycache__ hma_backend/__pycache__

test:
	FLASK_CONFIG="testing" python tests.py

