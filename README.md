DevOps Task Management App
Project Overview
This project is a Kubernetes-based Task Management web application composed of three Python Flask microservices: Task, Auth, and Notification. It is designed as a portfolio-grade DevOps project that simulates a production environment on a local Minikube cluster. The stack demonstrates containerization, Kubernetes deployments, CI/CD with GitHub Actions, observability with Prometheus and Grafana, centralized logging with the ELK stack, and security scanning of Docker images with Trivy.​

Architecture
Three microservices (Task, Auth, Notification) built with Flask and packaged as Docker images.​

Deployed to a local Minikube cluster using Kubernetes Deployments and NodePort Services in the default namespace.​

Monitoring via kube-prometheus-stack (Prometheus + Grafana) with ServiceMonitor resources scraping custom /metrics endpoints from each service.​

Centralized logging with Elasticsearch, Kibana, and a Fluent Bit DaemonSet in the logging namespace, shipping container logs to the fluent-bit index.​

CI/CD with GitHub Actions to build all microservice images and run Trivy vulnerability scans on every push to main.​

Tech Stack
Languages & Frameworks: Python, Flask.​

Containers & Orchestration: Docker, Kubernetes (Minikube), kubectl, Helm.​

CI/CD & Security: GitHub Actions, Trivy.​

Monitoring: Prometheus, Grafana, kube-prometheus-stack, ServiceMonitor CRDs.​

Logging: Elasticsearch, Kibana, Fluent Bit (DaemonSet).​

Local Setup (Minikube)
Start cluster and verify:

bash
minikube start
kubectl get nodes
The minikube node should be Ready.​

Build images locally (if not using a registry):

bash
cd services/task-service
docker build -t task-service:v1 .
cd ../auth-service
docker build -t auth-service:v1 .
cd ../notification-service
docker build -t notification-service:v1 .
Load into Minikube:

bash
minikube image load task-service:v1
minikube image load auth-service:v1
minikube image load notification-service:v1
Deploy microservices and services:

bash
kubectl apply -f k8s/
kubectl apply -f service.yaml
Access services:

bash
minikube service task-service --url
minikube service auth-service --url
minikube service notification-service --url
Use the printed URLs with /tasks, /health, and /metrics to exercise the app and generate metrics/logs.​

Monitoring (Prometheus & Grafana)
kube-prometheus-stack is installed into the monitoring namespace using the prometheus-community/kube-prometheus-stack Helm chart.​

Each Flask microservice exposes a /metrics endpoint using Prometheus client libraries with counters for request totals, histograms for latency, and domain-specific metrics (tasks created, login attempts, notifications sent).​

ServiceMonitor resources defined in servicemonitor.yaml select the three services (task-service, auth-service, notification-service) on ports 5000, 5001, and 5002 so Prometheus automatically discovers and scrapes them.​

Grafana connects to Prometheus as a data source and provides an “Application Services Monitoring” dashboard visualizing request rate, latency, and health across all three microservices.​

Centralized Logging (ELK + Fluent Bit)
The logging namespace hosts Elasticsearch and Kibana, deployed via Kubernetes manifests in the elk/ folder.​

Fluent Bit runs as a DaemonSet on all nodes, tails /var/log/containers for all pods, and sends logs to Elasticsearch using the fluent-bit index.​

Kibana is configured with a fluent-bit* data view using @timestamp as the time field, enabling centralized search and visualization of logs from task, auth, and notification services filtered by namespace or labels.​

CI/CD & Security (GitHub Actions + Trivy)
The workflow .github/workflows/ci.yml triggers on pushes and pull requests to main.​

CI job steps:

Check out repository and set up Docker Buildx.

Build Docker images for Task, Auth, and Notification services (task-service:latest, auth-service:latest, notification-service:latest).

Run Trivy scans for each image, failing the pipeline on CRITICAL/HIGH vulnerabilities to enforce a security gate.​

Successful runs are visible under the repository’s Actions → CI/CD Pipeline, providing an auditable history of builds and security scans.​

Screenshots
(Place actual image files under screenshots/ and update names if needed.)

Grafana dashboard for Task, Auth, and Notification services (screenshots/grafana-dashboard.png).

Kibana fluent-bit* Discover view showing centralized logs from all microservices (screenshots/kibana-logs.png).

GitHub Actions CI/CD pipeline run with Trivy scanning (screenshots/github-actions.png).​

Resume Highlights
Built a Kubernetes-based Task Management application with three Flask microservices, deployed on Minikube using Docker, Deployments, Services, and ServiceMonitors for observability.​

Implemented a GitHub Actions CI/CD pipeline to build all microservice images and run Trivy vulnerability scans on each container, enforcing a security gate on CRITICAL/HIGH issues before deployment.​

Set up end-to-end monitoring and centralized logging using Prometheus, Grafana, Elasticsearch, Kibana, and Fluent Bit to provide production-style visibility into application health and logs.​

