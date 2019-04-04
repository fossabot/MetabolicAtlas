<template>
  <section class="section section-no-top extended-section">
    <div class="container">
      <h3 class="title is-size-3">Comparison: {{ comparison.models.A.modelId }} vs {{ comparison.models.B.modelId }}</h3>
      <table class="is-fullwidth table is-narrow is-bordered">
        <thead>
          <tr>
            <th>Model</th>
            <th>Description</th>
            <th>Reactions</th>
            <th>Shared reactions</th>
            <th>Exclusive reactions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(model, key) in comparison.models">
            <td>{{ model.modelId }}</td>
            <td>{{ model.modelName }}</td>
            <td>{{ model.totalReactions }}</td>
            <td>{{ model.sharedReactions }}%</td>
            <td>{{ model.exclusiveReactions }}</td>
          </tr>
        </tbody>
      </table>
      If reactions modifiers are overlooked, another 4619 reactions would be shared between the two models.<br><br>

      <h5 class="title is-size-5">Ranked affected parts</h5>
      <div class="columns is-variable is-8">
        <div class="column">
          <h6 class="subtitle is-6">Subsystems by exclusive reactions</h6>
          <table class="table is-fullwidth is-striped is-hoverable">
            <thead>
              <tr>
                <th>Subsystem</th>
                <th>Reactions</th>
                <th>{{ comparison.models.A.modelId }}</th>
                <th>{{ comparison.models.B.modelId }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="subsys in comparison.subsystems">
                <td>{{ subsys.name }}</td>
                <td>{{ subsys.totalMissing }}</td>
                <td>{{ subsys.missingReactionsFromA }}</td>
                <td>{{ subsys.missingReactionsFromB }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="column">
          <h6 class="subtitle is-6">Compartments by exclusive reactions</h6>
          <table class="table is-fullwidth is-striped is-hoverable">
            <thead>
              <tr>
                <th>Compartments</th>
                <th>Reactions</th>
                <th>{{ comparison.models.A.modelId }}</th>
                <th>{{ comparison.models.B.modelId }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="subsys in comparison.compartments">
                <td>{{ subsys.name }}</td>
                <td>{{ subsys.totalMissing }}</td>
                <td>{{ subsys.missingReactionsFromA }}</td>
                <td>{{ subsys.missingReactionsFromB }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </section>

</template>

<script>

export default {
  name: 'compare-models',
  data() {
    return {
      comparison: {
        models: {
          A: {
            modelId: 'Human1',
            modelName: 'The generic genome-scale metabolic model of Homo sapiens integrated from HMR2 and Recon3D',
            totalReactions: 13774,
            sharedReactions: 59.34,
            exclusiveReactions: 5600,
          },
          B: {
            modelId: 'HMR2',
            modelName: 'Genome-scale metabolic model for the generic human cell',
            totalReactions: 8181,
            sharedReactions: 99.91,
            exclusiveReactions: 7,
          },
        },
        subsystems: [
          { name: 'Transport reactions',
            totalMissing: '1651',
            missingReactionsFromA: '1644',
            missingReactionsFromB: '7',
          },
          { name: 'Exchange/demand reactions',
            totalMissing: '1456',
            missingReactionsFromA: '1456',
            missingReactionsFromB: '-',
          },
          { name: 'Drug metabolism',
            totalMissing: '573',
            missingReactionsFromA: '573',
            missingReactionsFromB: '-',
          },
          { name: 'Fatty acid oxidation',
            totalMissing: '549',
            missingReactionsFromA: '549',
            missingReactionsFromB: '-',
          },
          { name: 'Fatty acid oxidation',
            totalMissing: '242',
            missingReactionsFromA: '242',
            missingReactionsFromB: '-',
          },
        ],
        compartments: [
          { name: 'Cytosol',
            totalMissing: '1692',
            missingReactionsFromA: '1676',
            missingReactionsFromB: '16',
          },
          { name: 'Extracellular',
            totalMissing: '372',
            missingReactionsFromA: '359',
            missingReactionsFromB: '13',
          },
          { name: 'Endoplasmic reticulum',
            totalMissing: '226',
            missingReactionsFromA: '225',
            missingReactionsFromB: '1',
          },
          { name: 'Boundary',
            totalMissing: '215',
            missingReactionsFromA: '204',
            missingReactionsFromB: '11',
          },
          { name: 'Lysosome',
            totalMissing: '162',
            missingReactionsFromA: '162',
            missingReactionsFromB: '0',
          },
        ],
      },
    };
  },
};
</script>

<style lang="scss"></style>
