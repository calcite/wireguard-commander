#!/bin/bash


trap term SIGTERM
trap term INT

term() {
  echo "Close VPN interfaces"
  for it in /etc/wireguard/*.conf; do
    wg-quick down "$it" || true
  done
}

for it in /etc/wireguard/*.conf; do
  wg-quick down "$it" || true
  wg-quick up "$it"
done

wgrest --static-auth-token "${SECRET:-secret}" --listen "0.0.0.0:${PORT:-8000}" &
wait $!
