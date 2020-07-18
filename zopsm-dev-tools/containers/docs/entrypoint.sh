#!/usr/bin/env sh

if [[ "$#" == 0 ]]; then
    echo "You should provide one of push, saas or roc."
    exit 1
fi


if [[ "$1" == "push" ]]; then
  cd /zopsm_docs
  touch status # for consul health check
  python /rest_api_render.py -u https://push.zops.io --service-name "Zops Unified Push Service API" --single-page --table-of-contents --output-file PUSH.md
  mkdir -p dist
  rm -rf /root/.grip

  if [[ "$GRIP_EXPORT" == "yes" ]]; then
     grip dist/PUSH.md --title "Zops Unified Push Service API" --export
  fi

  exit 0
fi

if [[ "$1" == "roc" ]]; then
  cd /zopsm_docs
  touch status # for consul health check
  python /rest_api_render.py -u https://gw.zops.io --service-name "Zops Realtime Online Chat Service API" --single-page --table-of-contents --output-file ROC.md
  mkdir -p dist
  rm -rf /root/.grip

  if [[ "$GRIP_EXPORT" == "yes" ]]; then
     grip dist/ROC.md --title "Zops Realtime Online Chat Service API" --export
  fi

  exit 0
fi

if [[ "$1" == "saas" ]]; then
  cd /zopsm_docs
  touch status # for consul health check
  python /rest_api_render.py -u https://saas.zops.io --service-name "Zops Saas API" --single-page --table-of-contents --output-file SAAS.md
  mkdir -p dist
  rm -rf /root/.grip

  if [[ "$GRIP_EXPORT" == "yes" ]]; then
     grip dist/SAAS.md --title "Zops Saas API" --export
  fi

  exit 0
fi

if [[ "$1" == "auth" ]]; then
  cd /zopsm_docs
  touch status # for consul health check
  python /rest_api_render.py -u https://auth.zops.io --service-name "Zops Auth API" --single-page --table-of-contents --output-file AUTH.md
  mkdir -p dist
  rm -rf /root/.grip

  if [[ "$GRIP_EXPORT" == "yes" ]]; then
     grip dist/AUTH.md --title "Zops Auth API" --export
  fi

  exit 0
fi