<template>
  <div>
    <h4 class="title is-size-4">References</h4>
    <p>Reference details are fetched dynamically from
      <a href="https://europepmc.org" target="_blank">Europe PMC</a>
      based on their PMID.
    </p>
    <template v-if="referenceList.length === 0">
      <p>There are no associated references.</p>
    </template>
    <template v-else>
      <br>
      <table class="main-table table is-fullwidth">
        <tr v-for="oneRef in referenceList" :key="oneRef.pmid">
          <td class="td-key has-background-primary has-text-white-bis">{{ oneRef.pmid }}</td>
          <td v-if="formattedRefs[oneRef.pmid]">
            <template v-if="formattedRefs[oneRef.pmid].link">
              <a target="_blank" :href="formattedRefs[oneRef.pmid].link">
                <span v-html="formattedRefs[oneRef.pmid].formattedString"></span>
              </a>
            </template>
            <template v-else>
              <span v-html="formattedRefs[oneRef.pmid].formattedString"></span>
            </template>
          </td>
          <td v-else>
            Not found in <a :href="`https://europepmc.org/search?query=${oneRef.pmid}`" target="_blank">Europe PMC</a>
          </td>
        </tr>
      </table>
    </template>
  </div>
</template>

<script>

import axios from 'axios';

export default {
  name: 'References',
  props: {
    referenceList: {
      type: Array,
      required: true,
    },
  },
  data() {
    return {
      formattedRefs: {},
    };
  },
  beforeMount() {
    if (this.referenceList.length > 0) {
      const queryIDs = `(EXT_ID:"${this.referenceList.map(e => e.pmid).join('"+OR+EXT_ID:"')}")`;
      axios.get(`https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=${queryIDs}&resultType=core&format=json`)
        .then((response) => {
          response.data.resultList.result.forEach((details) => {
            try {
              const refDetails = {};
              if (!details.fullTextUrlList) {
                refDetails.link = null;
              } else {
                refDetails.link = details.fullTextUrlList.fullTextUrl
                  .filter(e => e.documentStyle === 'html' && e.site === 'Europe_PMC');
                if (refDetails.link.length === 0) {
                  refDetails.link = details.fullTextUrlList.fullTextUrl.filter(
                    e => e.documentStyle === 'doi' || e.documentStyle === 'abs')[0].url;
                } else {
                  refDetails.link = refDetails.link[0].url;
                }
              }
              if (details.pubYear) {
                refDetails.year = details.pubYear;
              }
              refDetails.authors = details.authorList.author.map(e => e.fullName);
              refDetails.journal = details.journalInfo.journal.title;
              refDetails.title = details.title;
              refDetails.formattedString = `${refDetails.authors.join(', ')}, ${refDetails.year}. <i>${refDetails.title}</i> ${refDetails.journal}`;
              this.$set(this.formattedRefs, details.id, refDetails);
            } catch {
              // nothing
            }
          });
        });
    }
  },
};
</script>

<style lang="scss"></style>
