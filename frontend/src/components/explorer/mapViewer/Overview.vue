<template>
  <div class="column">
    <div id="heatmap"></div>
  </div>
</template>

<script>

import * as d3 from 'd3';

export default {
  name: 'Overview',
  props: ['model', 'maps'],
  components: {
  },
  data() {
    return {
      errorMessage: '',
      mapsUrl: {},
      data: [
        {
          c: 'Boundary',
          s: 'A subsystem',
          v: 1,
        }, {
          c: 'Boundary',
          s: 'B subsystem',
          v: 21,
        }, {
          c: 'E R',
          s: 'B subsystem',
          v: 20,
        },
      ],
    };
  },
  methods: {
    setup() {
      // set the dimensions and margins of the graph
      const margin = { top: 80, right: 25, bottom: 30, left: 40 };
      const width = 450 - margin.left - margin.right;
      const height = 450 - margin.top - margin.bottom;
      // append the svg object to the body of the page
      const svg = d3.select('#heatmap')
        .append('svg')
        .attr('width', width + margin.left + margin.right)
        .attr('height', height + margin.top + margin.bottom)
        .append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`);

      const myColumns = this.data.map(d => d.c);
      const myRows = this.data.map(d => d.s);

      // Build X scales and axis:
      const x = d3.scaleBand().range([0, width]).domain(myColumns).padding(0.05);
      svg.append('g')
        .style('font-size', 15)
        .attr('transform', `translate(0,${height})`)
        .call(d3.axisBottom(x).tickSize(0))
        .select('.domain')
        .remove();

      // Build Y scales and axis:
      const y = d3.scaleBand().range([height, 0]).domain(myRows).padding(0.05);
      svg.append('g')
        .style('font-size', 15)
        .call(d3.axisLeft(y).tickSize(0))
        .select('.domain')
        .remove();

      // Build color scale
      const myColor = d3.scaleSequential().interpolator(d3.interpolateInferno).domain([1, 100]);

      // create a tooltip
      const tooltip = d3.select('#my_dataviz')
        .append('div')
        .style('opacity', 0)
        .attr('class', 'tooltip')
        .style('background-color', 'white')
        .style('border', 'solid')
        .style('border-width', '2px')
        .style('border-radius', '5px')
        .style('padding', '5px');

      // Three function that change the tooltip when user hover / move / leave a cell
      const mouseover = () => {
        tooltip.style('opacity', 1);
        d3.select(this).style('stroke', 'black').style('opacity', 1);
      };
      const mousemove = (d) => {
        tooltip
          .html(`${d.v} reactions`)
          .style('left', `${d3.mouse(this)[0] + 70}px`)
          .style('top', `${d3.mouse(this)[1]}px`);
      };
      const mouseleave = () => {
        tooltip.style('opacity', 0);
        d3.select(this).style('stroke', 'none').style('opacity', 0.8);
      };

      // add the squares
      svg.selectAll()
        .data(this.data, d => d.v)
        .enter()
        .append('rect')
        .attr('x', d => x(d.c))
        .attr('y', d => y(d.s))
        .attr('rx', 4)
        .attr('ry', 4)
        .attr('width', x.bandwidth())
        .attr('height', y.bandwidth())
        .style('fill', d => myColor(d.v))
        .style('stroke-width', 4)
        .style('stroke', 'none')
        .style('opacity', 0.8)
        .on('mouseover', mouseover)
        .on('mousemove', mousemove)
        .on('mouseleave', mouseleave);
    },
  },
  mounted() {
    this.setup();
  },
};
</script>

<style lang="scss" scoped>
</style>
