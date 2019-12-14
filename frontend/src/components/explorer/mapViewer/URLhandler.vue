<template>
  <div>
  </div>
</template>

<script>
// import { idfy } from '../../../helpers/utils';
import { default as EventBus } from '../../../event-bus';

const EMPTY_PARAM = '_';
const DEFAULT_COORD = '0,0,0,0,0,0';

export default {
  name: 'URLhandler',
  props: {
    model: Object,
    mapType: String,
    mapName: String,
    dim: String,
    sel: Object,
    panel: Boolean,
  },
  data() {
    return {
      watchURL: true,
      search: null,
      coord: '0,0,0,0,0,0',
      g1: null,
      g2: null,
      currentURLParamsJSON: null,
      preventDimUpdate: false,
      URLparams: { path: {}, query: {} },
    };
  },
  computed: {
    // URLparams() {
    //   console.log('recomputed url parans');
    //   return {
    //     path: {
    //       mapType: this.mapType,
    //       mapName: this.mapName,
    //     },
    //     query: {
    //       dim: this.dim ? this.dim : '2d',
    //       panel: this.panel ? '1' : '0',
    //       sel: this.sel ? this.sel.id : EMPTY_PARAM,
    //       search: this.search ? this.search : EMPTY_PARAM,
    //       coord: this.coord,
    //       g1: this.g1 ? idfy(this.g1) : EMPTY_PARAM,
    //       g2: this.g2 ? idfy(this.g2) : EMPTY_PARAM,
    //     },
    //   };
    // },
  },
  watch: {
    /* eslint-disable quote-props */
    '$route': function watchSetup() {
      if (this.watchURL) {
        console.log('checkRoute watchURL');
        this.checkRoute();
      } else {
        this.watchURL = true;
      }
    },
    mapType: function f(v) {
      console.log('watch mapType change', v);
      if (v != null) {
        this.URLparams.path.mapType = v || null;
        this.updateURL(false, true);
      }
    },
    mapName: function f(v) {
      console.log('watch mapName change', v);
      if (v != null) {
        this.URLparams.path.mapName = v || null;
        this.updateURL(false, true);
      }
    },
    dim: function f(v) {
      console.log('watch dim change', v);
      this.URLparams.query.dim = v || '2d';
      if (!this.preventDimUpdate) {
        this.updateURL(false, false);
      } else {
        console.log('watch dim ignored');
        this.preventDimUpdate = false;
      }
    },
    panel: function f(v) {
      console.log('watch panel change', v);
      this.URLparams.query.panel = v ? '1' : '0';
      this.updateURL(true, false);
    },
    sel: function f(v) {
      console.log('watch sel change', v);
      this.URLparams.query.sel = v ? v.id : EMPTY_PARAM;
      this.updateURL(true, false);
    },
  },
  created() {
    EventBus.$off('checkRoute');
    EventBus.$off('update_url_coord');
    EventBus.$off('update_url_search');

    EventBus.$on('checkRoute', (v) => {
      console.log('here event checkRoute', v);
      this.checkRoute();
    });

    EventBus.$on('update_url_coord', (x, y, z, lx, ly, lz) => {
      console.log('update_url_coord', x, y, z, lx, ly, lz);
      if (x === null) {
        this.URLparams.query.coord = DEFAULT_COORD;
      } else {
        this.URLparams.query.coord = `${this.roundValue(x)},${this.roundValue(y)},${this.roundValue(z)},${this.roundValue(lx)},${this.roundValue(ly)},${this.roundValue(lz)}`;
      }
      this.updateURL(true, true);
    });

    EventBus.$on('update_url_search', (search) => {
      console.log('update_url_search', search);
      if (!search) {
        this.URLparams.query.search = EMPTY_PARAM;
      } else {
        this.URLparams.query.search = search;
      }
      this.updateURL(true, true);
    });
  },
  methods: {
    checkRoute() {
      // read the route parameters, validate, load the map or call function to process the parameters
      console.log('checkRoute');
      // load maps from url if contains map_id, the URL
      if (['viewerRoot', 'viewer'].includes(this.$route.name)) {
        this.getURLParameters(this.$route);
        console.log('URLparams2', this.URLparams);
        if (this.$route.query.prevent) { // TODO remove?
          console.log('checkRoute prevent');
          this.updateURL(true, true);
          return;
        }

        if (this.$route.name === 'viewerRoot') {
          // ignore maps param, '_' the others
          console.log('checkRoute viewerRoot stop');
          this.updateURL(false, false);
          return;
        }

        if (this.dim !== this.URLparams.query.dim) {
          // updating the url twice (first on map change) is breaking the path
          this.preventDimUpdate = true;
          EventBus.$emit('changeDimension');
        }

        if ((this.panel && this.URLparams.query.panel === '0')
            || (!this.panel && this.URLparams.query.panel === '1')) {
          // TOTO prevent url update?
          EventBus.$emit('togglePanel');
        }

        const searchTerm = this.URLparams.query.search === '_' ? '' : this.$route.query.search;
        const selectIDs = this.URLparams.query.sel === '_' ? [] : [this.URLparams.query.sel];

        this.$nextTick(() => {
          EventBus.$emit('showAction', this.URLparams.path.mapType, this.URLparams.path.mapName, searchTerm, selectIDs, this.URLparams.query.coord, false);
        });
      }
    },
    getURLParameters(route) {
      console.log('call getURLParamters');
      // valid some of the route parameters, set to default value if invalid
      if (route.name === 'viewer') {
        this.URLparams.path.mapType = this.$route.params.type;
        this.URLparams.path.mapName = this.$route.params.map_id;
      }

      if (!route.query) {
        this.URLparams.query = {
          dim: '2d',
          panel: '0',
          sel: EMPTY_PARAM,
          search: EMPTY_PARAM,
          coord: DEFAULT_COORD,
          g1: EMPTY_PARAM,
          g2: EMPTY_PARAM,
        };
        return;
      }

      const dim = route.query.dim && ['2d', '3d'].includes(route.query.dim.toLowerCase()) ? route.query.dim.toLowerCase() : '2d';
      const panel = route.query.panel && ['0', '1'].includes(route.query.panel) ? route.query.panel : '0';
      const regex = /(?:-)?\d+(?:[.]\d+)?(?:[,](?:-)?\d+(?:[.]\d+)?){5}/g;
      const coord = route.query.coord && route.query.coord.match(regex) ? route.query.coord : DEFAULT_COORD;

      this.URLparams.query = {
        dim,
        panel,
        sel: route.query.sel ? route.query.sel : EMPTY_PARAM,
        search: route.query.search ? route.query.search : EMPTY_PARAM,
        coord,
        g1: route.query.g1 ? route.query.g1 : EMPTY_PARAM,
        g2: route.query.g2 ? route.query.g1 : EMPTY_PARAM,
      };
    },
    updateURL(replace, newMapLoaded = false) {
      console.log('call updateURL');
      if (JSON.stringify(this.URLparams) === this.currentURLParamsJSON) {
        console.log('skip updateURL, no cahnge');
        return;
      }

      this.watchURL = false;
      let routeDict = null;
      if (this.$route.name === 'viewerRoot' && !newMapLoaded) {
        routeDict = {
          name: 'viewerRoot',
          params: {
            model: this.model.database_name,
          },
          query: this.URLparams.query,
        };
      } else {
        routeDict = { name: 'viewer',
          params: {
            model: this.model.database_name,
            type: this.URLparams.path.mapType,
            map_id: this.URLparams.path.mapName,
          },
          query: this.URLparams.query,
        };
      }
      console.log('new dict route', routeDict);
      if (replace) {
        this.$router.replace(routeDict).catch(() => {});
      } else {
        this.$router.push(routeDict).catch(() => {});
      }
      this.currentURLParamsJSON = JSON.stringify(this.URLparams);
    },
    roundValue(value) {
      return Math.round((value + 0.00001) * 1000) / 1000;
    },
  },
};
</script>

<style lang="scss"></style>
