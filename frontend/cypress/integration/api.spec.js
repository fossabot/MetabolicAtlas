/// <reference types="Cypress" />
context('API endpoints', () => {

  const APIbaseURL = '/api'
  const model = 'human1'

  describe('SingleComponentEndPoints', () => {
    it('Return single component JSON for Human1', () => {
      const urls = [
        [`${APIbaseURL}/${model}/reaction/HMR_1547`, 'api.reaction.HMR_1547'],
        [`${APIbaseURL}/${model}/metabolite/m02439c`, 'api.metabolite.m02439c'],
        [`${APIbaseURL}/${model}/compartment/nucleus`, 'api.compartment.nucleus'],
        [`${APIbaseURL}/hpa/gene/ENSG00000106636`, 'api.hpagene.ENSG00000106636'],
        [`${APIbaseURL}/${model}/gene/ENSG00000140795`, 'api.gene.ENSG00000140795'],
        [`${APIbaseURL}/${model}/subsystem/coa_catabolism`, 'api.subsystem.coa_catabolism'],
      ]

      urls.forEach(endpoint => {
        const url = endpoint[0];
        const jsonFile = endpoint[1];
        cy.request(url)
          .then(({headers, status, body}) => {
            expect(headers['content-type']).to.include('application/json')
            expect(status).to.eql(200)
            console.log(body)
            cy.fixture(`api/${jsonFile}`).then((jsonData) => {
              cy.log(JSON.stringify(jsonData))
              expect(body).to.eql(jsonData)
            })
          })
        })
      })
    })

  describe('MultiComponentEndPoints', () => {
    it('Return single component JSON for Human1', () => {
      const urls = [
        [`${APIbaseURL}/${model}/subsystems/`, 'api.subsystems'],
        [`${APIbaseURL}/${model}/reactions/`, 'api.reactions'],
        [`${APIbaseURL}/${model}/metabolites/`, 'api.metabolites'],
        [`${APIbaseURL}/${model}/genes/`, 'api.genes'],
        [`${APIbaseURL}/${model}/compartments/`, 'api.compartments'],
        [`${APIbaseURL}/hpa/genes/`, 'api.hpagenes'],
      ]

      urls.forEach(endpoint => {
        const url = endpoint[0];
        const jsonFile = endpoint[1];
        cy.request(url)
          .then(({headers, status, body}) => {
            expect(headers['content-type']).to.include('application/json')
            expect(status).to.eql(200)
            cy.fixture(`api/${jsonFile}`).then((jsonData) => {
              expect(body[0]).to.eql(jsonData)
            })
          })
        })
      })
    })

})
