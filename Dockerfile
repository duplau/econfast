FROM node:carbon

WORKDIR /usr/src/app

# package.json and package-lock.json
COPY package*.json ./

# Install app dependencies
RUN npm install

# Source code
COPY . .

CMD [ "npm", "start" ]