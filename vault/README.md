# Vault Integration Notes

This project includes a lightweight HashiCorp Vault profile to satisfy the secure-storage advanced feature in the SPE final project rubric.

## Start Vault

```bash
docker compose -f docker-compose.vault.yml up -d
```

Vault UI:

```text
http://localhost:8200
```

Development token:

```text
spe-dev-root
```

## Store Jenkins/Docker/Kubernetes Secrets

```bash
export VAULT_ADDR=http://localhost:8200
export VAULT_TOKEN=spe-dev-root

vault kv put secret/spe/dockerhub username="<dockerhub-user>" password="<dockerhub-token>"
vault kv put secret/spe/kubeconfig kubeconfig=@~/.kube/config
vault kv put secret/spe/app reload_token="<reload-token>"
```

## Evaluation Mapping

- Docker Hub credentials can be stored at `secret/spe/dockerhub`.
- Kubernetes deployment credentials can be stored at `secret/spe/kubeconfig`.
- Runtime app secrets can be stored at `secret/spe/app`.

For Jenkins, install the Vault plugin or fetch secrets before build stages. In production, replace the development Vault container with an initialized, sealed/unsealed Vault deployment and avoid committing real secrets.
