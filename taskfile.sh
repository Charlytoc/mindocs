#!/bin/bash

# Taskfile for managing docker-compose development environment

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored messages
print_message() {
    echo -e "${GREEN}[TASKFILE]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Help function
show_help() {
    echo "Usage: ./taskfile.sh [command]"
    echo ""
    echo "Commands:"
    echo "  dev       - Recreate and start all services (down + up)"
    echo "  up        - Start all services"
    echo "  down      - Stop all services"
    echo "  restart   - Restart all services"
    echo "  logs      - View logs from all services"
    echo "  logs-api  - View logs from API service"
    echo "  logs-worker - View logs from Worker service"
    echo "  shell     - Open shell in API container"
    echo "  migrate   - Run database migrations"
    echo "  seed      - Seed initial subscription plans"
    echo "  clean     - Stop and remove all containers, volumes, and images"
    echo "  ps        - Show running containers"
    echo "  help      - Show this help message"
}

# Main command handling
case "$1" in
    dev)
        print_message "Recreating development environment..."
        docker-compose down
        docker-compose up --build
        ;;
    up)
        print_message "Starting services..."
        docker-compose up
        ;;
    down)
        print_message "Stopping services..."
        docker-compose down
        ;;
    restart)
        print_message "Restarting services..."
        docker-compose restart
        ;;
    logs)
        docker-compose logs -f
        ;;
    logs-api)
        docker-compose logs -f api
        ;;
    logs-worker)
        docker-compose logs -f worker
        ;;
    shell)
        print_message "Opening shell in API container..."
        docker-compose exec api /bin/bash
        ;;
    migrate)
        print_message "Running database migrations..."
        docker-compose exec api alembic upgrade head
        ;;
    seed)
        print_message "Seeding subscription plans..."
        docker-compose exec api python management/seed_plans.py
        ;;
    clean)
        print_warning "This will remove all containers, volumes, and images!"
        read -p "Are you sure? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_message "Cleaning up..."
            docker-compose down -v --rmi all
            docker system prune -f
            print_message "Done!"
        else
            print_message "Cancelled."
        fi
        ;;
    ps)
        docker-compose ps
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
