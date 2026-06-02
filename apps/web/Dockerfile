FROM node:22-alpine

WORKDIR /app

COPY package.json package-lock.json ./
COPY apps/web/package.json ./apps/web/package.json
RUN npm install --workspace apps/web

COPY apps/web ./apps/web

EXPOSE 3000

WORKDIR /app/apps/web

CMD ["npm", "run", "dev"]
