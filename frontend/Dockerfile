FROM node:20-slim AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci || npm install
FROM node:20-slim AS builder
WORKDIR /app
ENV NODE_ENV=production
ENV NEXT_PUBLIC_API_URL=https://ai-tailor-backend-xxxxx.onrender.com
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build
FROM node:20-slim AS runner
WORKDIR /app
ENV NODE_ENV=production
ENV NEXT_PUBLIC_API_URL=https://ai-tailor-backend-xxxxx.onrender.com
COPY --from=builder /app ./
EXPOSE 3000
CMD bash -lc 'npm run start -- -p ${PORT:-3000}'
