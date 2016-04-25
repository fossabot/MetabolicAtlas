"""Update ReactionComponents with info from ExpressionData.

Use ExpressionData to set component_type and short_name on
ReactionComponents.
"""

import logging
import sys

from sqlalchemy import and_
import cobra

from hma_backend import db
from hma_backend.models import ReactionComponent, ExpressionData


logger = logging.getLogger(__name__)
sh = logging.StreamHandler(stream=sys.stderr)
logger.addHandler(sh)
formatter = logging.Formatter(("%(asctime)s - %(name)s - %(levelname)s - "
                               "%(message)s"))
sh.setFormatter(formatter)
logger.setLevel(logging.INFO)


def get_metabolites(gem_file):
    """Get (cobrapy) metabolites from gem_file."""
    cobra_model = cobra.io.read_sbml_model(gem_file)
    metabolites = set()
    logger.info("getting metabolites")
    for m in cobra_model.metabolites:
        # cobrapy strips prefix from IDs
        if m.id.startswith("m"):
            metabolites.add("M_" + m.id)
        else:
            metabolites.add(m.id)
    return metabolites


def main(gem_file):
    metabolites = get_metabolites(gem_file)

    for component in ReactionComponent.query.all():
        # FIXME rewrite?
        if component.id in metabolites:
            if component.long_name.startswith("ENSG0"):
                component.component_type = "enzyme"
            else:
                pass
                component.component_type = "metabolite"

        expr = ExpressionData.query.filter(
            and_(ExpressionData.gene_id == component.long_name,
                 ExpressionData.gene_name is not None)).first()
        if expr:
            # components *with* expression data, but *without* an ENSGID
            # should have type 'gene'
            if not component.long_name.startswith("ENSG0"):
                component.component_type = "gene"
            # use HPA data to set component short name
            component.short_name = expr.gene_name

        if not component.component_type:
            component.component_type = "compound"

        db.session.add(component)
        db.session.commit()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python update_component_info.py <gem_file>")
        sys.exit(1)
    main(sys.argv[1])
