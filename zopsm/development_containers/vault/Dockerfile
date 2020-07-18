FROM vault:0.11.1
RUN apk --no-cache add expect
COPY entrypoint.sh /entrypoint.sh
COPY run_vault.sh /run_vault.sh
COPY initialize.sh /initialize.sh
COPY start.sh /start.sh
RUN chmod +x entrypoint.sh && chmod +x initialize.sh && chmod +x run_vault.sh && chmod +x start.sh
CMD ["/start.sh"]
