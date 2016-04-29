import csv
import sys

from hma_backend import db
from hma_backend.models import ReactionComponent


def read_symbols(symbol_file):
    """Read symbols (short name) from file."""
    symbols = {}
    with open(symbol_file, 'r') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            gene_id = row['Ensembl Gene ID']
            symbol = row['HGNC symbol']
            symbols[gene_id] = symbol
        return symbols


def set_short_name(genes, symbols):
    """Update short_name where possible."""
    for gene in genes:
        if gene.long_name in symbols:
            gene.short_name = symbols[gene.long_name]
            db.session.add(gene)
    db.session.commit()


def main(symbol_file):
    symbols = read_symbols(symbol_file)
    genes = ReactionComponent.query.filter(
        ReactionComponent.long_name.like("ENSG0%")
    ).all()
    set_short_name(genes, symbols)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python add_short_names.py <symbol file>")
        sys.exit(1)
    main(sys.argv[1])
