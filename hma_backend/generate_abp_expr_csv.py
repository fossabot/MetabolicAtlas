"""Convert HPA antibody expression data to CSV.

The output CSV files are formatted for importing hma_backend
ExpressionData into PostgreSQL.
"""

from multiprocessing import Process, Queue, cpu_count
import csv
import logging
import sys

from hma_backend.models import ReactionComponent


NUM_CPUS = cpu_count()


logger = logging.getLogger(__name__)
sh = logging.StreamHandler(stream=sys.stderr)
logger.addHandler(sh)
formatter = logging.Formatter(("%(asctime)s - %(name)s - %(levelname)s - "
                               "%(message)s"))
sh.setFormatter(formatter)
logger.setLevel(logging.INFO)


def get_antibody_expressions(gene_ids, antibody_file):
    """Read antibody expressions from supplied file."""
    logger.info("Reading abp file...")
    q = Queue()
    queue_proc = Process(target=queue_abp_expressions,
                         args=(q, antibody_file, gene_ids, NUM_CPUS))
    queue_proc.start()
    workers = []
    for i in range(NUM_CPUS):
        worker = Process(target=save_abp_expression, args=(i, q))
        worker.start()
        workers.append(worker)
    logger.info("Reading abp file...done!")


def queue_abp_expressions(q, antibody_file, gene_ids, num_workers):
    """Read expressions from file and publish to a queue."""
    logger.info("Publish expressions")
    for expression in read_antibody_expressions(antibody_file):
        gene_id = expression['Gene']
        if gene_id in gene_ids:
            expression['id'] = gene_ids[gene_id]
            # FIXME what should we have here?
            expression['transcript_id'] = "N/A"
            # FIXME don't hardcode this
            expression['source'] = "HMA V14"
            q.put(expression)
    logger.info("Publisher done, notifying workers...")
    for i in range(num_workers):
        q.put("DONE!")
    logger.info("Workers notified")


def read_antibody_expressions(antibody_file):
    """Read expressions from file."""
    with open(antibody_file, 'r') as f:
        reader = csv.DictReader(f, delimiter=',', quotechar='"')
        for expression in reader:
            yield expression


def save_abp_expression(worker_id, q):
    """Read expressions from queue and save to CSV file.

    The output file is used to import data into PostgreSQL.
    """
    logger.info("Worker {0} started!".format(worker_id))
    with open("abp_expr_{0}.csv".format(worker_id), "w") as f:
        fields = ['id', 'Gene', 'Gene name', 'transcript_id', 'Tissue',
                  'Cell type', 'Level', 'Expression type', 'Reliability',
                  'source']
        writer = csv.DictWriter(f, delimiter=',', quotechar='"',
                                fieldnames=fields)
        while True:
            expression = q.get(True, 5)
            if expression == "DONE!":
                logger.info("Worker {0} done!".format(worker_id))
                break
            writer.writerow(expression)


def main(gem_file, antibody_file):
    # get expression data
    components = ReactionComponent.query.all()
    gene_ids = {component.long_name: component.id for component in components}

    logger.info("read abp expression data...")
    get_antibody_expressions(gene_ids, antibody_file)
    logger.info("read rnaseq expression data...done!")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(
            ("Usage: python generate_abp_expr_csv.py <gem_file> "
             "<antibody_file>")
        )
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])