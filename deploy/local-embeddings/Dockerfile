FROM node:20-bookworm-slim
WORKDIR /service
COPY package.json ./
RUN npm install --omit=dev --no-audit --no-fund
COPY server.mjs ./
USER node
ENV HOST=0.0.0.0 PORT=8080 MODEL_ROOT=/models MODEL_ID=MintplexLabs/multilingual-e5-small
EXPOSE 8080
CMD ["node", "server.mjs"]
