FROM node:lts-slim

RUN apt-key adv --fetch-keys http://dl.yarnpkg.com/debian/pubkey.gpg && echo "deb http://dl.yarnpkg.com/debian/ stable main" | tee /etc/apt/sources.list.d/yarn.list && apt-get update && apt-get install -y yarn --allow-unauthenticated && yarn global add webpack

WORKDIR /project/
ADD . .

EXPOSE 8080

RUN rm -rf node_modules && yarn
