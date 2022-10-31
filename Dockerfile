FROM odoo:15
USER root
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3-pip
ADD ./etc/requirements.txt /tmp/
RUN pip3 install pip --upgrade && \
    pip3 install --no-cache-dir -r /tmp/requirements.txt
USER odoo
