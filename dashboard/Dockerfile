FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
# We use npm run dev for development with Vite, mapping it to --host
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host"]
