FROM node:20-slim

RUN npm install -g tsx@4.19.1 \
    && useradd -ms /bin/bash runner

WORKDIR /workspace
USER runner

CMD ["node", "/workspace/solution.js"]
