from rest_framework import serializers
import api.models as APImodels
from django.db import models
from collections import defaultdict
import logging


def eid_to_dict(model):
    d = defaultdict(list)
    for el in model.external_databases.all():
        d[el.db_name].append({ 'id': el.external_id, 'url': el.external_link})
    return d


# inherited by CompartmentSerializer
# inherited by CompartmentMapViewerSerializer
# attr of SubsystemSearchSerializer
# attr of GeneReactionComponentSearchSerializer
# used in:
# private_view quick search
# views get_compartment (CompartmentSerializer)
# views get_compartments (CompartmentSerializer)
# private_views get_data_viewer (CompartmentMapViewerSerializer)
class CompartmentBasicSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='name_id')

    class Meta:
        model = APImodels.Compartment
        fields = ('id', 'name',)


# inherited by CompartmentMapViewerSerializer
# used in:
# views get_compartment
# views get_compartments
# private_views get_data_viewer (CompartmentMapViewerSerializer)
class CompartmentSerializer(CompartmentBasicSerializer):
    id = serializers.CharField(source='name_id')

    class Meta(CompartmentBasicSerializer.Meta):
        fields = CompartmentBasicSerializer.Meta.fields + \
         ('letter_code', 'metabolite_count', 'gene_count', 'reaction_count', 'subsystem_count')


# used in:
# private_views get_data_viewer
class CompartmentMapViewerSerializer(CompartmentBasicSerializer):
    compartment_svg = serializers.SlugRelatedField(
        read_only=True,
        slug_field='name_id',
    )

    class Meta(CompartmentBasicSerializer.Meta):
        fields = CompartmentBasicSerializer.Meta.fields + ('compartment_svg', 'reaction_count')


# used in:
# private_views get_data_viewer
class CompartmentSvgSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='name_id')
    compartment = serializers.SlugRelatedField(
        slug_field='name_id',
        read_only=True,
    )
    # subsystems = serializers.SlugRelatedField(
    #     many=True,
    #     read_only=True,
    #     slug_field='name',
    #     source="subsystem"
    #  )

    class Meta:
        model = APImodels.CompartmentSvg
        fields = ('id', 'name', 'compartment', 'filename', 'reaction_count', 'sha')

# =========================================================================================

# inherited by SubsystemSearchSerializer
# inherited by SubsystemMapViewerSerializer
# attr of GeneReactionComponentSearchSerializer
# used in:
# views get_compartment
# private views search quick search
# private_views search global search (SubsystemSearchSerializer)
# private_views get_data_viewer (SubsystemMapViewerSerializer)
class SubsystemBasicSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='name_id')

    class Meta:
        model = APImodels.Subsystem
        fields = ('id', 'name',)


# inherited by SubsystemSerializer
# used in:
# private_views search global search
# views get_subsystem (SubsystemSerializer)
class SubsystemSearchSerializer(SubsystemBasicSerializer):
    compartments = CompartmentBasicSerializer(many=True, read_only=True, source="compartment")

    class Meta(SubsystemBasicSerializer.Meta):
        fields = SubsystemBasicSerializer.Meta.fields + \
        ('reaction_count', 'metabolite_count', 'gene_count', 'compartments',)


# used in:
# views get_subsystem
class SubsystemSerializer(SubsystemSearchSerializer):
    external_databases = serializers.SerializerMethodField()

    class Meta(SubsystemSearchSerializer.Meta):
        fields = SubsystemSearchSerializer.Meta.fields + \
        ('unique_metabolite_count', 'compartment_count', 'external_databases',)

    def get_external_databases(self, model):
        return eid_to_dict(model)


# used in:
# private_views get_data_viewer
class SubsystemMapViewerSerializer(SubsystemBasicSerializer):
    subsystem_svg = serializers.SlugRelatedField(
        read_only=True,
        slug_field='name_id',
    )

    class Meta(SubsystemBasicSerializer.Meta):
        fields = SubsystemBasicSerializer.Meta.fields + ('subsystem_svg', 'reaction_count')


# used in:
# private_views get_data_viewer
class SubsystemSvgSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='name_id')
    subsystem = serializers.SlugRelatedField(
        slug_field='name_id',
        read_only=True,
    )

    class Meta:
        model = APImodels.SubsystemSvg
        fields = ('id', 'name', 'subsystem', 'filename', 'reaction_count', 'sha')
