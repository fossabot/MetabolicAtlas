<template>
  <div v-if="externalDbs && Object.keys(externalDbs).length !== 0">
    <h4 class="title is-4">External databases</h4>
    <table id="ed-table" class="table is-fullwidth">
      <template v-for="k in extDbListOrdered">
        <tr :key="k">
          <td class="td-key has-background-primary has-text-white-bis">{{ reformatTableKey(k) }}</td>
          <td>
            <template v-for="(el, index) in externalDbs[k]">
              <template v-if="index !== 0">{{ ', ' }}</template>
              <template v-if="el.url">
                <a :href="`${el.url}`" target="_blank" :key="el.id">{{ el.id }}</a>
              </template>
              <template v-else>
                {{ el.id }}
              </template>
            </template>
          </td>
        </tr>
      </template>
    </table>
  </div>
</template>

<script>
import { reformatTableKey } from '../../../helpers/utils';

export default {
  name: 'ExtIdTable',
  props: {
    externalDbs: Object,
  },
  computed: {
    extDbListOrdered() {
      return Object.keys(this.externalDbs).sort();
    },
  },
  methods: {
    reformatTableKey,
  },
};
</script>

<style lang="scss"></style>
