FROM python:3.10

RUN adduser algo && usermod -aG algo algo

USER algo

ARG PS1='"\u@\h:\W$ "'

RUN echo "export PS1=$PS1" >> ~/.bashrc

RUN echo "export PYTHONPATH=~/workspace/src:$PYTHONPATH" >> ~/.bashrc

RUN echo "set editing-mode emacs" >> ~/.inputrc
RUN echo "set completion-ignore-case off" >> ~/.inputrc
RUN echo "set show-all-if-unmodified on" >> ~/.inputrc
RUN echo '"\\C-p": history-search-backward' >> ~/.inputrc
RUN echo '"\\C-n": history-search-forward' >> ~/.inputrc
RUN echo '"\\e[A": history-search-backward' >> ~/.inputrc
RUN echo '"\\e[B": history-search-forward' >> ~/.inputrc

WORKDIR ~/workspace

COPY requirements.txt .

RUN pip3 install -r requirements.txt
