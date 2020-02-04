/// <reference types="Cypress" />
context('API endpoints', () => {

  describe('SingleCompoEndPoints', () => {
    const APIbaseURL = '/api'
    const model = 'human1'
    urls = [
        [`${APIbaseURL}/${model}/reaction/HMR_1547`, 'api.reaction.HMR_1547'],
        [`${APIbaseURL}/${model}/metabolite/m02439c`, 'api.metabolite.m02439c'],
        [`${APIbaseURL}/${model}/gene/ENSG00000106636`, 'api.gene.ENSG00000106636'],
        [`${APIbaseURL}/${model}/compartment/nucleus`, 'api.compartment.nucleus'],
        [`${APIbaseURL}/${model}/subsystem/pyruvate_metabolism`, 'api.subsystem.pyruvate'],
        [`${APIbaseURL}/${model}/hpa/gene/ENSG00000106636`, 'api.hpagene.ENSG00000106636'],
    ]

    cy.server()
    urls.forEach((url, jsonFile) => {
        cy.route({method: 'GET', url: url}).as('apiCall')
        cy.wait('@apiCall').then(function(xhr) {
          const response = xhr.responseBody
          cy.fixture(`api/${jsonFile}`).as('jsonData')
          expect(response).to.eql('@jsonData')
        })
    }
  })

  describe('MultiCompoEndPoints', () => {
    const APIbaseURL = '/api'
    const model = 'human1'
    urls = [
        [`${APIbaseURL}/${model}/reactions/`, 'api.reactions'],
        [`${APIbaseURL}/${model}/metabolites/`, 'api.metabolites'],
        [`${APIbaseURL}/${model}/genes/`, 'api.genes'],
        [`${APIbaseURL}/${model}/compartments/`, 'api.compartments'],
        [`${APIbaseURL}/${model}/subsystems/`, 'api.subsystems'],
        [`${APIbaseURL}/${model}/hpa/genes/`, 'api.hapgenes'],
    ]

    cy.server()
    urls.forEach((url, jsonFile) => {
        cy.route({method: 'GET', url: url}).as('apiCall')
        cy.wait('@apiCall').then(function(xhr) {
          const response = xhr.responseBody
          cy.fixture(`api/${jsonFile}`).as('jsonData')
          expect(response.length).to.be.at.least(2)
          expect(response[0]).to.eql('@jsonData')
        })
    }
  })

})
