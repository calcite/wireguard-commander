FROM alpine:3.19

RUN addgroup -S wgui && \
    adduser -S -D -G wgui wgui

RUN apk --no-cache add ca-certificates wireguard-tools jq iptables curl

RUN curl -L https://github.com/suquant/wgrest/releases/latest/download/wgrest-linux-amd64 -o /usr/local/bin/wgrest && \
    chmod +x /usr/local/bin/wgrest

COPY init.sh /init.sh

RUN chmod +x /init.sh

EXPOSE 8000/tcp

ENTRYPOINT ["/init.sh"]
