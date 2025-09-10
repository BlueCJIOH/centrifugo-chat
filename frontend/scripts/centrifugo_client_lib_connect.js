'use strict'

// Connect to Centrifugo using official client library.
// - Mints connection token (HS256) for user_id=5 with CF_TOKEN_SECRET.
// - Connects to ws://localhost:8001/connection/websocket

globalThis.WebSocket = require('ws')
const { Centrifuge } = require('centrifuge')
const jwt = require('jsonwebtoken')

const USER_ID = process.env.USER_ID || '5'
const WS_URL = process.env.WS_URL || 'ws://localhost:8001/connection/websocket'
const CF_TOKEN_SECRET = process.env.CF_TOKEN_SECRET || 'a4f2#p4=$5cd1)=xahh12r_sv(1g8jls&m-(zlja1&^8@2a%a0'
const TOKEN_TTL_SECONDS = Number(process.env.TOKEN_TTL_SECONDS || 120)

function mintConnectionToken(userId) {
  const now = Math.floor(Date.now() / 1000)
  return jwt.sign({ sub: String(userId), exp: now + TOKEN_TTL_SECONDS }, CF_TOKEN_SECRET, { algorithm: 'HS256' })
}

const token = mintConnectionToken(USER_ID)
console.log('[cfg] ws =', WS_URL)
console.log('[cfg] user_id =', USER_ID)

const centrifuge = new Centrifuge(WS_URL, { token })

centrifuge.on('connected', (ctx) => {
  console.log('[centrifuge] connected', ctx)
})
centrifuge.on('error', (err) => {
  console.error('[centrifuge] error', err)
})
centrifuge.on('disconnected', (ctx) => {
  console.log('[centrifuge] disconnected', ctx)
})

centrifuge.connect()

setTimeout(() => {
  centrifuge.disconnect()
}, 5000)


