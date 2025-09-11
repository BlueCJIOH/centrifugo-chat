'use strict'

// Simple Centrifugo WS connect test that:
// 1) Mints a connection token (HS256) with sub='5'
// 2) Connects to ws://localhost:8001/connection/websocket using 'centrifuge-json'
// 3) Subscribes to channel personal:5 with a generated subscription token

const WebSocket = require('ws')
const fetch = require('node-fetch')
const jwt = require('jsonwebtoken')

const USER_ID = process.env.USER_ID || '5'
const WS_URL = process.env.WS_URL || 'ws://localhost:8001/connection/websocket'
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:9002'
const APP_JWT = process.env.APP_JWT || 'a4f2#p4=$5cd1)=xahh12r_sv(1g8jls&m-(zlja1&^8@2a%a0'
const CHANNEL = process.env.CHANNEL || `personal:${USER_ID}`

async function getConnectionToken(appJwt) {
  const r = await fetch(BACKEND_URL + '/api/token/connection/', {
    headers: { Authorization: 'Bearer ' + appJwt }
  })
  if (!r.ok) {
    const text = await r.text()
    throw new Error('connection token request failed: ' + r.status + ' ' + text)
  }
  const d = await r.json()
  return d.token
}

async function getSubscriptionToken(appJwt, channel) {
  const r = await fetch(BACKEND_URL + '/api/token/subscription/?channel=' + encodeURIComponent(channel), {
    headers: { Authorization: 'Bearer ' + appJwt }
  })
  if (!r.ok) {
    const text = await r.text()
    throw new Error('subscription token request failed: ' + r.status + ' ' + text)
  }
  const d = await r.json()
  return d.token
}

async function main() {
  if (!APP_JWT) {
    console.error('Set APP_JWT env var (Bearer from your auth service)')
    process.exit(2)
  }

  console.log('[cfg] ws =', WS_URL)
  console.log('[cfg] backend =', BACKEND_URL)
  console.log('[cfg] user_id =', USER_ID)
  console.log('[cfg] channel =', CHANNEL)

  const connectionToken = await getConnectionToken(APP_JWT)
  try {
    const decodedConn = jwt.decode(connectionToken)
    console.log('[dbg] connect token sub/exp:', decodedConn && { sub: decodedConn.sub, exp: decodedConn.exp })
  } catch (_) {}

  const subscriptionToken = await getSubscriptionToken(APP_JWT, CHANNEL)

  const ws = new WebSocket(WS_URL, 'centrifuge-json', { perMessageDeflate: false })

  ws.on('open', () => {
    console.log('[ws] open → sending connect')
    const frame = { id: 1, connect: { token: connectionToken } }
    ws.send(JSON.stringify(frame))
  })

  ws.on('message', (data) => {
    const text = Buffer.isBuffer(data) ? data.toString('utf8') : data
    try {
      const msg = JSON.parse(text)
      if (msg.connected) {
        console.log('[ws] connected:', msg.connected)
        ws.send(JSON.stringify({ subscribe: { channel: CHANNEL, token: subscriptionToken } }))
        return
      }
      if (msg.ping) {
        ws.send('{"pong":{}}')
        return
      }
      if (msg.subscribed) {
        console.log('[ws] subscribed:', msg.subscribed)
        return
      }
      if (msg.publication) {
        console.log('[ws] publication:', msg.publication)
        return
      }
      console.log('[ws] message:', msg)
    } catch (e) {
      console.log('[ws] raw:', text)
    }
  })

  ws.on('error', (err) => {
    console.error('[ws] error:', err && err.message ? err.message : err)
  })

  ws.on('close', (code, reason) => {
    const why = reason && reason.toString ? reason.toString() : ''
    console.log('[ws] close', code, why)
  })

  ws.on('ping', () => {
    try { ws.pong() } catch (_) {}
  })
}

main().catch((e) => {
  console.error('fatal:', e)
  process.exit(1)
})


