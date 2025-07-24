# My Kubernetes Operator

This project is a Python-based Kubernetes operator built with the [Kopf](https://kopf.readthedocs.io/) framework.

## Overview

The operator manages `AppDeployment` custom resources, which define the desired state of a simple web application. The operator will create, update, and delete Kubernetes `Deployments` and `Services` to match the state of the `AppDeployment` resources.

## CRD Schema

The `AppDeployment` CRD has the following schema:

- `spec.replicas`: (integer) The number of replicas for the application.
- `spec.image`: (string) The container image to use for the application.
- `spec.port`: (integer) The port to expose on the container.
- `spec.expose`: (boolean) Whether to expose the application with a Kubernetes Service.
- `spec.checkIntervalSeconds`: (integer) How often to run a periodic check on the deployment's pods.

## How to Use

### Build and Deploy the Operator

1.  **Build the Docker image:**

    ```bash
    docker build -t your-docker-registry/appdeployment-operator:latest .
    ```

2.  **Push the image to a registry:**

    ```bash
    docker push your-docker-registry/appdeployment-operator:latest
    ```

3.  **Update the operator deployment manifest:**

    In `manifests/operator-deployment.yaml`, replace `your-docker-registry/appdeployment-operator:latest` with the actual image name.

4.  **Deploy the operator:**

    ```bash
    kubectl apply -f crds/appdeployment-crd.yaml
    kubectl apply -f manifests/operator-deployment.yaml
    ```

### Apply a Sample CR

1.  **Apply the sample `AppDeployment` resource:**

    ```bash
    kubectl apply -f manifests/sample-cr.yaml
    ```

### Observe Effects and Logs

1.  **Check the operator logs:**

    ```bash
    kubectl logs -l app=appdeployment-operator -f
    ```

2.  **Check the created resources:**

    ```bash
    kubectl get appdeployments
    kubectl get deployments
    kubectl get services
    kubectl get pods
    ```

3.  **Observe the status updates on the `AppDeployment` resource:**

    ```bash
    kubectl get appdeployment my-app -o yaml
    ```

### Run Tests

1.  **Install development dependencies:**

    ```bash
    pip install -r requirements.txt
    pip install pytest pytest-asyncio pytest-mock
    ```

2.  **Run the tests:**

    ```bash
    pytest
    ```

## Sample CR Manifest

```yaml
apiVersion: "myorg.io/v1"
kind: AppDeployment
metadata:
  name: my-app
  namespace: default
spec:
  replicas: 2
  image: "nginx:latest"
  port: 80
  expose: true
  checkIntervalSeconds: 30
```
