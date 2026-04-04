FROM alpine:latest
RUN apk add --no-cache curl bash unzip
RUN curl -L -o /v2ray.zip https://github.com/v2fly/v2ray-core/releases/latest/download/v2ray-linux-64.zip && \
    unzip /v2ray.zip && chmod +x /v2ray && rm /v2ray.zip
COPY config.json /config.json
CMD /v2ray run -config /config.json
