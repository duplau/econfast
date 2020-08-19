const { client, index_publi, index_author, checkConnection } = require('./connection')

module.exports = {
  queryTerm (term, offset = 0) {
    const body = {
      from: offset,
      sort: [
        {"influence": "desc"},
        "_score"
      ],
      query: { 
        bool: {
          should: [
              { match: { 'full_name': { query: term, boost: 64, operator: 'and', fuzziness: 'auto' } } },
              { match: { 'institutions': { query: term, boost: 16, operator: 'and', fuzziness: 'auto' } } },
              { match: { 'jel-labels-fr': { query: term, boost: 8, operator: 'and' } } },
              { match: { 'jel-labels-en': { query: term, boost: 8, operator: 'and' } } },
              { match: { 'keywords': { query: term, boost: 8, operator: 'and' } } },
              { match: { 'titles':    { query: term, boost: 4, operator: 'and', fuzziness: 'auto' } } },
              // { match: { 'abstracts': { query: term, boost: 2, operator: 'and', fuzziness: 'auto' } } },
              // TODO negative boost for aptonyms (i.e. author names which are a common economics term...)
          ]
        }
      },
      highlight: { fields: { text: {} } }
    }
    return client.search({ index: index_author, body: body })
  },

  getPubli (pub_id) {
    const body = {
      query: { 
        ids: {
          "values": [pub_id]
        }
      }
    }
    return client.search({ index: index_publi, body: body })
  }  
}
