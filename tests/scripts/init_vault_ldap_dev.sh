docker compose -f "`dirname $0`"/../config_files/vault-ldap/docker-compose-dev.yml up -d vault openldap
sleep 5
terraform -chdir="`dirname $0`"/../config_files/vault-ldap init
terraform -chdir="`dirname $0`"/../config_files/vault-ldap apply -auto-approve