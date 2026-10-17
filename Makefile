.PHONY: install test build run-backend run-frontend sample-data docker-up clean help

help:
	@echo "Available make commands:"
	@echo "  make install      - Install backend and frontend dependencies"
	@echo "  make test         - Run all backend unit & integration tests"
	@echo "  make build        - Compile TypeScript and bundle frontend"
	@echo "  make run-backend  - Start FastAPI backend server on :8000"
	@echo "  make run-frontend - Start Vite frontend dev server on :3000"
	@echo "  make sample-data  - Generate pre-computed demo snapshots and comparisons"
	@echo "  make docker-up    - Build and launch all services with Docker Compose"

install:
	cd backend && pip install -r requirements.txt
	cd frontend && npm install

test:
	python -m pytest backend/tests -v

build:
	cd frontend && npm run build

run-backend:
	uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload

run-frontend:
	cd frontend && npm run dev

sample-data:
	python scripts/generate_sample_data.py

docker-up:
	docker-compose up --build
