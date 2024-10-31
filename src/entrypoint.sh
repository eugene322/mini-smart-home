#!/bin/bash
# No more than 100 lines of code
wait_for () {
    for _ in `seq 0 100`; do
        (echo > /dev/tcp/$1/$2) >/dev/null 2>&1
        if [[ $? -eq 0 ]]; then
            echo "$1:$2 accepts connections!^_^"
            break
        fi
        sleep 1
    done
}
populate_env_variables () {
  set -o allexport
  [[ -f /src/core/.env ]] && source /src/core/.env
  set +o allexport
  echo "env variables are populated!^_^"
}
populate_env_variables
case "$PROCESS" in
"LINT")
    mypy . && flake8 . && bandit -r . --exclude tests
    ;;
"TEST")
    pytest -v --cov .
    ;;
"BOT")
    python core/run_bot.py
    ;;
"WORKER")
    python core/worker.py
    ;;
*)
    echo "NO PROCESS SPECIFIED!>_<"
    exit 1
    ;;
esac
