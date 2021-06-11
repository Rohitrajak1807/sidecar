FROM python
ENV APP_DIR=/opt/sidecar
ARG HOST_IP
RUN mkdir -p $APP_DIR
COPY requirements.txt "$APP_DIR"/
RUN bash -c "cd $APP_DIR && python -m venv ./venv && source ./venv/bin/activate && echo 'source /opt/sidecar/venv/bin/activate' >> /root/.bashrc && pip install -r requirements.txt"
RUN apt update && apt install sshpass -y
RUN bash -c "ssh-keygen -t rsa -N '' -f /root/.ssh/id_rsa"
RUN cat /root/.ssh/id_rsa.pub
RUN sshpass -f /run/secrets/pass ssh-copy-id -o StrictHostKeyChecking=no -i /root/.ssh/id_rsa.pub $(cat /run/secrets/user_name)@"$HOST_IP"