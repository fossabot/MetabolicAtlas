FROM neo4j:4.1.0

COPY ./plugins /plugins
RUN rm -r /var/lib/neo4j/data
COPY ./data /var/lib/neo4j/data
