ARG VARIANT="3.10-bullseye"
FROM mcr.microsoft.com/vscode/devcontainers/python:0-${VARIANT}

RUN adduser algo && usermod -aG algo algo

WORKDIR /app

USER algo

RUN echo "export PROMPT_DIRTRIM=2" >> ~/.bashrc
RUN echo 'export PS1="\w$ "' >> ~/.bashrc

RUN echo "export PYTHONPATH=~/app/src:$PYTHONPATH" >> ~/.bashrc

RUN echo "set editing-mode emacs" >> ~/.inputrc
RUN echo "set completion-ignore-case off" >> ~/.inputrc
RUN echo "set show-all-if-unmodified on" >> ~/.inputrc
RUN echo '"\\C-p": history-search-backward' >> ~/.inputrc
RUN echo '"\\C-n": history-search-forward' >> ~/.inputrc
RUN echo '"\\e[A": history-search-backward' >> ~/.inputrc
RUN echo '"\\e[B": history-search-forward' >> ~/.inputrc

COPY requirements.txt .

RUN pip3 install -r requirements.txt
