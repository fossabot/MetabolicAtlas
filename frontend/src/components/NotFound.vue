<template>
  <div class="column has-text-centered is-three-fifths-desktop is-three-quarters-tablet is-fullwidth-mobile">
    <div class="box has-background-light content">
      <template v-if="component">
        <p class="title is-size-3">
          <span class="is-capitalized">{{ component }}&nbsp;</span> "&nbsp;{{ componentId }}&nbsp;" &nbsp;not found
        </p>
        <template v-if="component === 'model'">
          <p>Visit the Explore page to select one of our integrated models</p>
        </template>
        <template v-else>
          <p class="is-size-5">
            Probably there is a typo in the {{ component }} identifier in the URL
            <br>Use the search bar above to find other {{ component }}s
          </p>
        </template>
      </template>
      <template v-else>
        <h1 class="is-size-1 has-text-weight-bold">¯\_(ツ)_/¯<br>404</h1><br>
        <p class="is-size-5">
          The page requested does not exist on this
          <router-link :to="{ path: '/about#5-September-2019' }"><b>new version of Metabolic Atlas</b></router-link><br>
          If you are looking to download a GEM, look in the menu for
          <router-link :to="{ name: 'gems' }"><b>GEM > Repository</b></router-link>
        </p>
        <br>
      </template>
    </div>
  </div>
</template>
<script>

export default {
  name: 'NotFound',
  props: {
    component: String,
    componentId: String,
  },
};

</script>

<style>
</style>
