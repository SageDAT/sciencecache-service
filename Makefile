MAGICK_HOME=/usr/local/opt/imagemagick@6
run-service:
	SCIENCECACHE_SERVICE_ROOT=./ MAGICK_HOME=$(MAGICK_HOME) gunicorn sciencecache-service:app --reload

run-stack:
	docker-compose up -d

tests:
	python tests.py

stage:
	rm -rf dist
	mkdir dist
	cp config.beta.json config.prod.json dist
	cp *.py dist
	cp sciencecache-service.wsgi dist
	cp requirements.txt dist
	cp -R requirements dist

