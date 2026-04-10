FROM alpine:latest

# تثبيت الأدوات اللازمة
RUN apk add --no-cache curl unzip

# تحميل وتشغيل v2ray-core
RUN curl -L -o /v2ray.zip https://github.com/v2fly/v2ray-core/releases/latest/download/v2ray-linux-64.zip && \
    unzip /v2ray.zip && \
    chmod +x /v2ray && \
    rm /v2ray.zip

# نسخ الإعدادات داخل الحاوية
COPY config.json /config.json

# تشغيل السيرفر على المنفذ 8080
CMD /v2ray run -config /config.json
