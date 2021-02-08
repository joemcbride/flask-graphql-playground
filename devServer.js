const express = require('express')
const webpack = require('webpack')
const webpackDevMiddleware = require('webpack-dev-middleware')
const { createProxyMiddleware } = require('http-proxy-middleware')

let app = express()

const config = require('./webpack.config.js')
let compiler = webpack(config)

app.use(webpackDevMiddleware(compiler))
app.use(require('webpack-hot-middleware')(compiler))

app.use(
  '/',
  createProxyMiddleware({
    target: 'http://localhost:5000/',
  })
)

const port = 9000
app.listen(port, () => console.log(`Webpack server running at http://localhost:${port}`))
