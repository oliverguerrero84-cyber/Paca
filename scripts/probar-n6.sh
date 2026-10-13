# Prueba de N6 /guardar-envio: lo prende, guarda un envío a sucursal en el pedido abierto de
# «Prueba Paca» y lo vuelve a apagar pase lo que pase. Los flujos de n8n viven apagados.
# «Prueba Paca» necesita un pedido abierto: correr antes `bash scripts/probar-n1.sh`.
# Lo corre una persona con `!`: el clasificador de Claude Code no deja prender flujos.
# Uso: bash scripts/probar-n6.sh [branch_code] [sucursal]   (lee N8N_API_URL y N8N_API_KEY del entorno)
[ -z "$N8N_API_KEY" ] && [ -f "$HOME/.n8n-korvance.env" ] && { set -a; . "$HOME/.n8n-korvance.env"; set +a; }
: "${N8N_API_URL:?falta N8N_API_URL}" "${N8N_API_KEY:?falta N8N_API_KEY}"
A="${N8N_API_URL%/}/api/v1"; W=7Q8UyEgDhxIkVdSy   # N6 · Envío del pedido
trap 'curl -s -X POST "$A/workflows/$W/deactivate" -H "X-N8N-API-KEY: $N8N_API_KEY" -o /dev/null -w "N6 apagado: %{http_code}\n"' EXIT
curl -s -X POST "$A/workflows/$W/activate" -H "X-N8N-API-KEY: $N8N_API_KEY" -o /dev/null -w "N6 prendido: %{http_code}\n"
curl -s -X POST "${N8N_API_URL%/}/webhook/guardar-envio" -H 'Content-Type: application/json' \
  -d "{\"contactId\":\"1IzcksRfvxpnEohAZSg5\",\"modalidad\":\"sucursal\",\"branch_code\":\"${1:-PRUEBA01}\",\"sucursal\":\"${2:-Sucursal de prueba}\"}"; echo
