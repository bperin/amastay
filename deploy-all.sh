#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Setup logging
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_DIR="logs"
MAIN_LOG="${LOG_DIR}/deploy_${TIMESTAMP}.log"

# Function to setup logging
setup_logging() {
    mkdir -p "$LOG_DIR"
    echo "=== Deployment Started at $(date) ===" | tee -a "$MAIN_LOG"
    echo "Log files will be saved in: $LOG_DIR" | tee -a "$MAIN_LOG"
}

# Function to log messages
log_message() {
    local level=$1
    local message=$2
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${timestamp} [${level}] ${message}" | tee -a "$MAIN_LOG"
}

# Function to check AWS credentials
check_aws_credentials() {
    log_message "INFO" "Checking AWS credentials..."
    if ! aws sts get-caller-identity &>/dev/null; then
        log_message "ERROR" "AWS credentials not configured properly"
        exit 1
    fi
    local aws_account=$(aws sts get-caller-identity --query Account --output text)
    log_message "INFO" "Using AWS Account: ${aws_account}"
}

# Function to deploy a service to all environments
deploy_service() {
    local service=$1
    local service_log="${LOG_DIR}/${service}_${TIMESTAMP}.log"

    log_message "INFO" "Starting deployment of ${service}"
    log_message "INFO" "Detailed logs for ${service} will be in: ${service_log}"

    # Log environment info
    echo "=== Environment Information for ${service} ===" >>"$service_log"
    echo "Timestamp: $(date)" >>"$service_log"
    echo "Working Directory: $(pwd)" >>"$service_log"
    echo "User: $(whoami)" >>"$service_log"
    echo "=== Deployment Start ===" >>"$service_log"

    copilot svc deploy --name "$service" --env production --env staging --env develop --yes 2>&1 | tee -a "$service_log" &
    echo $! >"/tmp/${service}_pid"

    log_message "INFO" "Deployment process started for ${service} with PID $(cat /tmp/${service}_pid)"
}

# Function to monitor deployment status
monitor_deployment() {
    local service=$1
    local pid=$(cat "/tmp/${service}_pid")
    local service_log="${LOG_DIR}/${service}_${TIMESTAMP}.log"
    local start_time=$(date +%s)

    log_message "INFO" "Monitoring deployment of ${service} (PID: ${pid})"

    while kill -0 $pid 2>/dev/null; do
        local current_time=$(date +%s)
        local elapsed=$((current_time - start_time))

        echo -e "${BLUE}${service}:${NC} Deployment in progress... (${elapsed}s elapsed)"
        copilot svc status --name "$service" 2>&1 | tee -a "$service_log"

        # Get and log resource usage
        echo "=== Resource Usage at $(date) ===" >>"$service_log"
        copilot svc show "$service" 2>&1 >>"$service_log"

        sleep 10
    done

    wait $pid
    local exit_code=$?

    if [ $exit_code -eq 0 ]; then
        log_message "SUCCESS" "${service} deployment completed successfully after ${elapsed}s"
        echo "=== Final Status ===" >>"$service_log"
        copilot svc status --name "$service" >>"$service_log"
    else
        log_message "ERROR" "${service} deployment failed after ${elapsed}s with exit code ${exit_code}"
        echo "=== Deployment Failed ===" >>"$service_log"
        echo "Exit Code: ${exit_code}" >>"$service_log"
        cat "$service_log"
        exit 1
    fi
}

# Function to check service health
check_service_health() {
    local service=$1
    local environment=$2
    local health_log="${LOG_DIR}/${service}_health_${TIMESTAMP}.log"

    log_message "INFO" "Checking health for ${service} in ${environment}"

    # Get the service endpoint
    local endpoint=$(copilot svc show -n "$service" -e "$environment" --json | jq -r '.routes[0].url')

    if [ -n "$endpoint" ]; then
        log_message "INFO" "Testing endpoint: ${endpoint}/api/v1/health/check"
        curl -s -o /dev/null -w "%{http_code}" "${endpoint}/api/v1/health/check" >>"$health_log"
    else
        log_message "WARNING" "Could not determine endpoint for ${service} in ${environment}"
    fi
}

# Cleanup function
cleanup() {
    log_message "INFO" "Cleaning up temporary files..."
    rm -f /tmp/*_pid

    # Archive logs older than 7 days
    find "$LOG_DIR" -type f -name "*.log" -mtime +7 -exec gzip {} \;

    log_message "INFO" "Deployment logs archived in ${LOG_DIR}"
}

# Main deployment script
main() {
    setup_logging
    check_aws_credentials

    log_message "INFO" "Starting parallel deployment of all services..."

    # Start deployments in parallel
    for service in "backend-app" "frontend-app" "scraper-app"; do
        deploy_service "$service"
    done

    # Monitor all deployments
    log_message "INFO" "Monitoring deployments..."
    for service in "backend-app" "frontend-app" "scraper-app"; do
        monitor_deployment "$service"
    done

    # Check health of all services in all environments
    log_message "INFO" "Performing health checks..."
    for service in "backend-app" "frontend-app" "scraper-app"; do
        for env in "production" "staging" "develop"; do
            check_service_health "$service" "$env"
        done
    done

    cleanup

    log_message "SUCCESS" "All deployments completed successfully!"
    echo -e "${GREEN}Deployment completed! Logs available in: ${LOG_DIR}${NC}"
}

# Trap errors
trap 'log_message "ERROR" "An error occurred. Check logs for details."; cleanup; exit 1' ERR

# Run the script
main
