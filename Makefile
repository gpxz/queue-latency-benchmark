pip-compile:
	pip-compile --upgrade --resolver backtracking --output-file requirements.txt requirements.in

up:
	docker-compose up --build --remove-orphans --rm