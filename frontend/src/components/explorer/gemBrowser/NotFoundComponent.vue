<template>
  <div class="column has-text-centered"
      :class="component ? 'is-three-fifths-desktop is-three-quarters-tablet is-fullwidth-mobile' : 'is-narrow'">
    <div class="box has-background-light content">
      <template v-if="component">
        <p class="title is-size-3">
          <span class="is-capitalized">{{ component }}&nbsp;</span> "&nbsp;{{ componentID }}&nbsp;" &nbsp;not found
        </p>
        <template v-if="component === 'model'">
          <p>Visit the Explore page to select one of our integrated models</p>
        </template>
        <template v-else>
          <p class="is-size-5">
            Probably there is a typo in the {{ component }} identifier in the URL
            <br>Use the search bar to find other {{ component }}s
          </p>
        </template>
      </template>
      <template v-else>
        <p>The page requested does not exist on this<br><b>new version of Metabolic Atlas</b></p>
        <p>If you are looking to download a GEM,<br>look in the menu for <b>GEM > Repository</b></p>
        <h1 class="is-size-1 has-text-weight-bold">¯\_(ツ)_/¯ 404</h1>
      </template>
    </div>
  </div>
</template>
<script>

export default {
  name: 'NotFoundComponent',
  props: {
    component: String,
    componentID: String,
  },
};

</script>

<style>
</style>
