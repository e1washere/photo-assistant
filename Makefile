.PHONY: install run test clean docker-build docker-run

install:
	pip install -r requirements.txt

run:
	python run_streamlit.py

test:
	python main.py --demo

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf static/uploads/*

docker-build:
	docker build -t photo-assistant .

docker-run:
	docker run -p 8501:8501 photo-assistant

docker-compose-up:
	docker-compose up -d

docker-compose-down:
	docker-compose down 