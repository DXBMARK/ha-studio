# HA Studio command-line tools as a container image (read-only tools; no Home Assistant access unless you pass HA_URL/HA_TOKEN).
# (c) 2026 DXBMARK LLC - Apache-2.0
FROM python:3.12-slim
LABEL org.opencontainers.image.title="ha-studio" \
      org.opencontainers.image.description="Plan, design and generate business-grade dashboards compatible with Home Assistant" \
      org.opencontainers.image.source="https://github.com/DXBMARK/ha-studio" \
      org.opencontainers.image.licenses="Apache-2.0" \
      org.opencontainers.image.vendor="DXBMARK LLC"
RUN pip install --no-cache-dir PyYAML==6.0.3
COPY skills/ha-studio /opt/ha-studio
COPY docker/ha-studio /usr/local/bin/ha-studio
RUN chmod +x /usr/local/bin/ha-studio && useradd -m -u 10001 hastudio
USER hastudio
WORKDIR /work
ENTRYPOINT ["ha-studio"]
CMD ["--help"]
