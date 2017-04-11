import sys, os

from django.db import models
from api.models import ReactionComponent, Reaction, CurrencyMetabolite

from django.core.management.base import BaseCommand

def readTextFileAndAdd(cm_file):
    cm_to_add = []
    with open(cm_file, 'r') as f:
        for line in f:
            tokens = line.strip().split(",")
            component_id = "M_" + tokens[0]
            reaction_ids = ["R_" + reaction for reaction in tokens[1:]]
            component = ReactionComponent.objects.filter(id=component_id)
            if(len(component)!=1):
                sys.exit("No component found for id "+component_id)
            for reaction_id in reaction_ids:
                reaction = Reaction.objects.filter(id=reaction_id)
                if(len(reaction)!=1):
                    sys.exit("No reaction found for id "+reaction_id)
                cm = CurrencyMetabolite(component=component[0], reaction=reaction[0])
                cm_to_add.append(cm)
    CurrencyMetabolite.objects.bulk_create(cm_to_add)



class Command(BaseCommand):
    args = '<foo bar ...>'
    help = 'our help string comes here'

    def handle(self, *args, **options):
        readTextFileAndAdd("/Users/halena/Documents/Sys2Bio/hma-prototype/database_generation/data/currencyMets.csv")