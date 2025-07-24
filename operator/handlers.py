import kopf
import kr8s
import logging


@kopf.on.create('myorg.io', 'v1', 'appdeployments')
def create_fn(spec, name, namespace, logger, **kwargs):
    """Create and manage an AppDeployment."""
    api = kr8s.api()
    deployment = {
        'apiVersion': 'apps/v1',
        'kind': 'Deployment',
        'metadata': {
            'name': name,
            'namespace': namespace,
            'labels': {'app': name}
        },
        'spec': {
            'replicas': spec.get('replicas', 1),
            'selector': {'matchLabels': {'app': name}},
            'template': {
                'metadata': {'labels': {'app': name}},
                'spec': {
                    'containers': [{
                        'name': name,
                        'image': spec['image'],
                        'ports': [{'containerPort': spec['port']}]
                    }]
                }
            }
        }
    }
    kopf.adopt(deployment)
    api.create(deployment)

    if spec.get('expose', False):
        service = {
            'apiVersion': 'v1',
            'kind': 'Service',
            'metadata': {'name': name, 'namespace': namespace},
            'spec': {
                'selector': {'app': name},
                'ports': [{'port': spec['port'], 'targetPort': spec['port']}],
                'type': 'ClusterIP'
            }
        }
        kopf.adopt(service)
        api.create(service)

    logger.info(f"AppDeployment {name} created.")
    return {'status': 'created'}


@kopf.on.update('myorg.io', 'v1', 'appdeployments')
def update_fn(spec, status, name, namespace, logger, **kwargs):
    """Handle updates to the AppDeployment."""
    api = kr8s.api()
    deployment = api.get('deployment', name, namespace=namespace)
    deployment.spec.replicas = spec.get('replicas', 1)
    deployment.spec.template.spec.containers[0].image = spec['image']
    deployment.spec.template.spec.containers[0].ports[0].containerPort = spec['port']
    api.patch(deployment)

    if spec.get('expose', False):
        if not api.get('service', name, namespace=namespace):
            service = {
                'apiVersion': 'v1',
                'kind': 'Service',
                'metadata': {'name': name, 'namespace': namespace},
                'spec': {
                    'selector': {'app': name},
                    'ports': [{'port': spec['port'], 'targetPort': spec['port']}],
                    'type': 'ClusterIP'
                }
            }
            kopf.adopt(service)
            api.create(service)
        else:
            service = api.get('service', name, namespace=namespace)
            service.spec.ports[0].port = spec['port']
            service.spec.ports[0].targetPort = spec['port']
            api.patch(service)
    else:
        if api.get('service', name, namespace=namespace):
            api.delete('service', name, namespace=namespace)

    logger.info(f"AppDeployment {name} updated.")
    return {'status': 'updated'}


@kopf.on.delete('myorg.io', 'v1', 'appdeployments')
def delete_fn(name, namespace, logger, **kwargs):
    """Handle deletion of the AppDeployment."""
    api = kr8s.api()
    try:
        api.delete('deployment', name, namespace=namespace)
        logger.info(f"Deployment {name} deleted.")
    except kr8s.NotFoundError:
        logger.warning(f"Deployment {name} not found, already deleted.")

    try:
        api.delete('service', name, namespace=namespace)
        logger.info(f"Service {name} deleted.")
    except kr8s.NotFoundError:
        pass  # Service might not exist

    logger.info(f"AppDeployment {name} deleted.")
    return {'status': 'deleted'}


@kopf.timer('myorg.io', 'v1', 'appdeployments', interval='spec.checkIntervalSeconds')
def check_pods(spec, name, namespace, status, logger, **kwargs):
    """Periodically check the number of pods."""
    api = kr8s.api()
    try:
        deployment = api.get('deployment', name, namespace=namespace)
        pod_count = deployment.status.get('readyReplicas', 0)

        if pod_count < spec.get('replicas', 1):
            message = f"Warning: Deployment {name} has {pod_count} pods, but {spec.get('replicas', 1)} are expected."
            logger.warning(message)
            kopf.event(kwargs['body'], type="Warning", reason="MissingReplicas", message=message)
            return {'status': message}
        else:
            logger.info(f"Deployment {name} has {pod_count} pods.")
            return {'status': f"OK: {pod_count} pods running."}

    except kr8s.NotFoundError:
        logger.error(f"Deployment {name} not found during check.")
        raise kopf.TemporaryError(f"Deployment {name} not found.", delay=60)
