# Prueba de N1 de punta a punta: lo prende, lo llama una vez con «Prueba Paca» (sku de test 1,
# 1 pieza) y lo vuelve a apagar pase lo que pase. Los flujos de n8n viven apagados.
# Lo corre una persona con `!`: el clasificador de Claude Code no deja prender flujos.
# Uso: bash scripts/probar-n1.sh   (lee N8N_API_URL y N8N_API_KEY del entorno)
[ -z "$N8N_API_KEY" ] && [ -f "$HOME/.n8n-korvance.env" ] && { set -a; . "$HOME/.n8n-korvance.env"; set +a; }
: "${N8N_API_URL:?falta N8N_API_URL}" "${N8N_API_KEY:?falta N8N_API_KEY}"
A="${N8N_API_URL%/}/api/v1"; W=fFvyuDEo7oLB1vIb   # N1 · Apartar
trap 'curl -s -X POST "$A/workflows/$W/deactivate" -H "X-N8N-API-KEY: $N8N_API_KEY" -o /dev/null -w "N1 apagado: %{http_code}\n"' EXIT
curl -s -X POST "$A/workflows/$W/activate" -H "X-N8N-API-KEY: $N8N_API_KEY" -o /dev/null -w "N1 prendido: %{http_code}\n"
curl -s -X POST "${N8N_API_URL%/}/webhook/apartar" -H 'Content-Type: application/json' \
  -d '{"sku":"PV-MUJ-BOU","cantidad":1,"contactId":"1IzcksRfvxpnEohAZSg5"}'; echo
