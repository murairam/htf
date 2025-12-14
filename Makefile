.PHONY: help install dev prod fastapi all-services stop-services check-services clean fclean rebuild test migrate

# Colors for output
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(GREEN)Available commands:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-15s$(NC) %s\n", $$1, $$2}'

install: ## Install all dependencies (Python + Node.js)
	@echo "$(GREEN)Installing Python dependencies...$(NC)"
	pip install -r requirements.txt
	@echo "$(GREEN)Installing Node.js dependencies...$(NC)"
	cd frontend && npm install
	@echo "$(GREEN)Running migrations...$(NC)"
	python manage.py migrate
	@echo "$(GREEN)Installation complete!$(NC)"

dev: ## Start development servers (Django + React + FastAPI)
	@echo "$(GREEN)Starting development servers...$(NC)"
	@echo "$(YELLOW)Django: http://localhost:8000$(NC)"
	@echo "$(YELLOW)React: http://localhost:5173$(NC)"
	@echo "$(YELLOW)FastAPI: http://localhost:8001$(NC)"
	./run_dev.sh

prod: ## Start production server (Django serving React build)
	@echo "$(GREEN)Building frontend...$(NC)"
	cd frontend && npm run build
	@echo "$(GREEN)Collecting static files...$(NC)"
	python manage.py collectstatic --noinput
	@echo "$(GREEN)Starting production server...$(NC)"
	@echo "$(YELLOW)Access: http://localhost:8000$(NC)"
	./run_prod.sh

api-agent: ## Start only API_Final_Agent service
	@echo "$(GREEN)Starting API_Final_Agent service...$(NC)"
	@echo "$(YELLOW)Access: http://localhost:8001$(NC)"
	cd API_Final_Agent && python main.py

all-services: rebuild ## Start all services (API_Final_Agent + Django) with fresh frontend build
	@echo "$(GREEN)Starting all services...$(NC)"
	@echo "$(YELLOW)Django: http://localhost:8000$(NC)"
	@echo "$(YELLOW)API_Final_Agent: http://localhost:8001$(NC)"
	./run_all_services.sh

stop-services: ## Stop all background services
	@echo "$(GREEN)Stopping all services...$(NC)"
	./stop_all_services.sh

check-services: ## Check status of all services
	./check_services.sh

rebuild: ## Rebuild frontend and collect static files
	@echo "$(GREEN)Rebuilding frontend...$(NC)"
	cd frontend && npm run build
	@echo "$(GREEN)Copying frontend build to Django static...$(NC)"
	cp -r frontend/dist/* backend/static/react/
	@echo "$(GREEN)Collecting static files...$(NC)"
	python manage.py collectstatic --noinput
	@echo "$(GREEN)Frontend rebuild complete!$(NC)"

migrate: ## Run database migrations
	@echo "$(GREEN)Running migrations...$(NC)"
	python manage.py makemigrations
	python manage.py migrate
	@echo "$(GREEN)Migrations complete!$(NC)"

clean: ## Clean build artifacts and cache files
	@echo "$(YELLOW)Cleaning build artifacts...$(NC)"
	rm -rf frontend/dist
	rm -rf frontend/node_modules/.vite
	rm -rf staticfiles
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)Clean complete!$(NC)"

fclean: clean ## Full clean (including dependencies and database)
	@echo "$(RED)Full clean - removing all dependencies and database...$(NC)"
	rm -rf frontend/node_modules
	rm -rf venv
	rm -rf .venv
	rm -f db.sqlite3
	rm -rf media/uploads/*
	@echo "$(GREEN)Full clean complete!$(NC)"

test: ## Run tests
	@echo "$(GREEN)Running Python tests...$(NC)"
	python manage.py test
	@echo "$(GREEN)Tests complete!$(NC)"

shell: ## Open Django shell
	python manage.py shell

superuser: ## Create Django superuser
	python manage.py createsuperuser

logs: ## Show recent logs (if using systemd or similar)
	@echo "$(YELLOW)Showing recent application logs...$(NC)"
	tail -f logs/*.log 2>/dev/null || echo "No log files found"

check: ## Run Django system checks
	@echo "$(GREEN)Running system checks...$(NC)"
	python manage.py check
	@echo "$(GREEN)Checks complete!$(NC)"

format: ## Format code (Python with black, JS with prettier)
	@echo "$(GREEN)Formatting Python code...$(NC)"
	black . --exclude venv 2>/dev/null || echo "black not installed, skipping..."
	@echo "$(GREEN)Formatting JavaScript code...$(NC)"
	cd frontend && npx prettier --write "src/**/*.{js,jsx}" 2>/dev/null || echo "prettier not installed, skipping..."
	@echo "$(GREEN)Formatting complete!$(NC)"

status: check-services ## Alias for check-services

.DEFAULT_GOAL := help
