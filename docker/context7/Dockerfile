FROM node:20-alpine

RUN npm install -g @upstash/context7-mcp@2.1.2

EXPOSE 3010

ENV CONTEXT7_PORT=3010

CMD ["sh", "-c", "context7-mcp --transport http --port ${CONTEXT7_PORT} ${CONTEXT7_API_KEY:+--api-key ${CONTEXT7_API_KEY}}"]