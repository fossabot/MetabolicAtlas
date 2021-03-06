<template>
  <router-link class="tile is-parent" :class="size"
               :to="{ name: 'browser', params: { model: model.database_name, type: type, id: data.id } }">
    <div class="tile is-child clickable box hoverable"
         :title="`Click to view ${data.name || data.id}`">
      <p class="is-capitalized subtitle is-size-4-desktop is-size-5-tablet
         has-text-weight-light has-text-grey-light">{{ type }}</p>
      <template v-if="type === 'metabolite'">
        <span class="is-capitalized"><b>{{ data.name }}</b></span>
        with {{ model.short_name }} ID <b>{{ data.id }}</b> is in
        the <b>{{ data.compartment }}</b> compartment.
        <p v-if="data.formula">Its formula is <b>{{ data.formula }}</b>.</p>
        <p v-if="data.reaction_count">This compound is involved in
          <b>{{ data.reaction_count }}</b> reaction(s) across the model.
        </p>
      </template>
      <template v-else-if="type === 'reaction'">
        <b>{{ data.id }}</b> is <b>{{ data.is_reversible ? 'reversible' : 'irreversible' }}</b>
        and has the following equation:
        <br>
        <b>{{ data.equation_wname.replace('=>', data.is_reversible ? '&#8660;' : '&#8658;') }}</b>.
        <br><br>
        This reaction is part of <b>{{ data.subsystem_count }}</b> subsystem(s)
        and <b>{{ data.compartment_count }}</b> compartment(s) and is associated
        with <b>{{ data.gene_count }}</b> gene(s).
      </template>
      <template v-else-if="type === 'compartment'">
        <span class="is-capitalized"><b>{{ data.name }}</b></span> has
        <b>{{ data.reaction_count }}</b> reactions,
        <b>{{ data.metabolite_count }}</b> metabolite(s) and
        <b>{{ data.gene_count }}</b> gene(s).
        <br><br>
        <b>Major subsystems</b>:
        <br>
        <p><ul><li v-for="sub in data.subsystems" :key="sub">{{ sub }}</li></ul></p>
      </template>
      <template v-else-if="type === 'subsystem'">
        <b>{{ data.name }}</b> has <b>{{ data.reaction_count }}</b> reaction(s),
        <b>{{ data.metabolite_count }}</b> metabolite(s) and
        <b>{{ data.gene_count }}</b> gene(s).
        This subsystem spans across <b>{{ data.compartment_count }}</b> compartment(s).
      </template>
      <template v-else>
        <template v-if="data.name">
          <b>{{ data.name }}</b> with {{ model.short_name }} ID <b>{{ data.id }}</b>
          is associated with <b>{{ data.reaction_count }}</b> reaction(s) across
          <b>{{ data.subsystem_count }}</b> subsystem(s) and
          <b>{{ data.compartment_count }}</b> compartment(s).
        </template>
        <template v-else>
          <b>{{ data.id }}</b> is associated with
          <b>{{ data.reaction_count }}</b> reaction(s) across
          <b>{{ data.subsystem_count }}</b> subsystem(s) and
          <b>{{ data.compartment_count }}</b> compartment(s).
        </template>
      </template>
      <slot></slot>
    </div>
  </router-link>
</template>

<script>
import { mapState } from 'vuex';

export default {
  name: 'Tile',
  props: {
    type: String,
    data: Object,
    size: String,
  },
  computed: {
    ...mapState({
      model: state => state.models.model,
    }),
  },
};
</script>

<style lang="scss"></style>
