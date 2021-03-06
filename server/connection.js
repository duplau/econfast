const elasticsearch = require('elasticsearch')

const index_publi = 'publication_a'
const index_author = 'author_a'
const port = 9200
const host = process.env.ES_HOST || 'localhost'
const client = new elasticsearch.Client({ host: { host, port } })

async function checkConnection () {
  let isConnected = false
  while (!isConnected) {
    console.log('Connecting to ES')
    try {
      const health = await client.cluster.health({})
      console.log(health)
      isConnected = true
    } catch (err) {
      console.log('Connection Failed, Retrying...', err)
    }
  }
}

// checkConnection()


module.exports = {
  client, index_publi, index_author, checkConnection
}