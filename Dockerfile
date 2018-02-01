# arxiv/zero

# For production:
FROM 626657773168.dkr.ecr.us-east-1.amazonaws.com/arxiv/base:latest

#For local testing:
# FROM arxiv-base:latest 

WORKDIR /opt/arxiv/

ADD requirements.txt Pipfile Pipfile.lock /opt/arxiv/
RUN pip install -U pip && \
  pip install -r /opt/arxiv/requirements.txt && \
  pipenv install

ENV PATH "/opt/arxiv:${PATH}"

ADD wsgi.py uwsgi.ini /opt/arxiv/
ADD zero/ /opt/arxiv/zero/

EXPOSE 8000

CMD pipenv run uwsgi --ini uwsgi.ini
