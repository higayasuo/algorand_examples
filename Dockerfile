FROM python:3

RUN adduser algo && usermod -aG algo algo

USER algo

ARG PS1='"\u@\h:\W$ "'

RUN echo "export PS1=$PS1" >> ~/.bashrc

WORKDIR ~/workspace

COPY requirements.txt .

RUN pip3 install -r requirements.txt