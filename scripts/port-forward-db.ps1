# Port-forward PostgreSQL from Kubernetes cluster to localhost
# Run this in a separate terminal when you need to connect to ogbrain DB from laptop
# Then set .env: DATABASE_URL=postgresql://hari:isys969isys969@localhost:5432/ogmoney
# and PGVECTOR_ENABLED=true

kubectl port-forward -n ogbrain-dev-infra-pgvector svc/pg-cluster-rw 5432:5432
