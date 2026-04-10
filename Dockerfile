FROM alpine:latest

# تحديث وتثبيت الأدوات اللازمة
RUN apk add --no-cache curl unzip bash

# تحميل محرك التشغيل (v2ray)
RUN curl -L -o /v2ray.zip https://github.com/v2fly/v2ray-core/releases/latest/download/v2ray-linux-64.zip && \
    unzip /v2ray.zip && \
    chmod +x /v2ray && \
    rm /v2ray.zip

# نسخ ملف الإعدادات إلى الحاوية
COPY config.json /config.json

# تشغيل السيرفر على المنفذ المخصص للمنصات المجانية
CMD /v2ray run -config /config.json
