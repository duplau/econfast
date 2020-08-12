const Koa = require('koa')
const Router = require('koa-router')
const joi = require('joi')
const validate = require('koa-joi-validate')
const search = require('./search')

const app = new Koa()
const router = new Router()

app.use(async (ctx, next) => {
  const start = Date.now()
  await next()
  const ms = Date.now() - start
  console.log(`${ctx.method} ${ctx.url} - ${ms}`)
})

app.on('error', err => {
  console.error('Server Error', err)
})

app.use(async (ctx, next) => {
  ctx.set('Access-Control-Allow-Origin', '*')
  return next()
})

router.get('/search',
  validate({
    query: {
      term: joi.string().max(512).required(),
      offset: joi.number().integer().min(0).default(0)
    }
  }),
  async (ctx, next) => {
    const { term, offset } = ctx.request.query
    ctx.body = await search.queryTerm(term, offset)
  }
)

router.get('/publi',
  validate({
    query: {
      publi_id: joi.string().max(256).required()
    }
  }),
  async (ctx, next) => {
    const { publi_id } = ctx.request.query
    ctx.body = await search.getPubli(publi_id)
  }
)

const port = process.env.PORT || 3000

app
  .use(router.routes())
  .use(router.allowedMethods())
  .listen(port, err => {
    if (err) throw err
    console.log(`EconFast API listening on ${port}`)
  })
