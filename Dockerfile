FROM python
ENV APP_DIR=/opt/sidecar
RUN mkdir -p $APP_DIR
COPY . $APP_DIR/
WORKDIR $APP_DIR
RUN pip install -r requirements.txt
RUN apt update && apt install sshpass -y
RUN bash -c "ssh-keygen -t rsa -N '' -f /root/.ssh/id_rsa"
ARG USER
ARG SSHPASS
ARG HOST_IP
RUN sshpass -e ssh-copy-id -o StrictHostKeyChecking=no -i /root/.ssh/id_rsa.pub "$USER"@"$HOST_IP"
RUN echo "StrictHostKeyChecking no" >> /etc/ssh/ssh_config
CMD bash -c "source /root/.bashrc && python $APP_DIR/main.py"