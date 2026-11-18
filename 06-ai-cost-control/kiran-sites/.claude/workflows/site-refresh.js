export const meta = {
  name: 'site-refresh',
  description: 'Kiran Studio monthly site refresh for one client: read the request, build the change, critic checks it against data/<client>.json, write the report.',
  whenToUse: 'When a client sends the monthly site refresh request. Pass the client slug, e.g. mehr-bakery.',
  phases: [
    { title: 'Read', detail: 'reader: request + data file -> list of changes' },
    { title: 'Build', detail: 'builder: edit the page, run check-site.py until it passes' },
    { title: 'Critic', detail: 'critic: page vs data/<client>.json -> APPROVED / REJECTED' },
    { title: 'Report', detail: 'reporter: short job report in reports/' },
  ],
}

// The client slug arrives as structured args or as free text ("for client mehr-bakery").
const raw = typeof args === 'string' ? args : JSON.stringify(args || '')
const m = raw.match(/[a-z]+(?:-[a-z]+)+/)
const client = (args && typeof args === 'object' && args.client) ? args.client : (m ? m[0] : '')
if (!/^[a-z]+(-[a-z]+)*$/.test(client)) {
  throw new Error('site-refresh: no client slug in args (got ' + raw + ')')
}
log('client: ' + client)

const CHANGES = {
  type: 'object',
  properties: {
    changes: { type: 'array', items: { type: 'object', properties: {
      what: { type: 'string' }, new_value: { type: 'string' } }, required: ['what', 'new_value'] } },
  },
  required: ['changes'],
}
const BUILD = {
  type: 'object',
  properties: {
    changed: { type: 'array', items: { type: 'string' } },
    checker_passed: { type: 'boolean' },
    last_checker_output: { type: 'string' },
  },
  required: ['changed', 'checker_passed', 'last_checker_output'],
}
const VERDICT = {
  type: 'object',
  properties: {
    verdict: { type: 'string', enum: ['APPROVED', 'REJECTED'] },
    mismatches: { type: 'array', items: { type: 'string' } },
    note: { type: 'string' },
  },
  required: ['verdict', 'mismatches', 'note'],
}

phase('Read')
const req = await agent(
  'Client: ' + client + '. Read requests/' + client + '.md and data/' + client + '.json. List every change the client asks for.',
  { agentType: 'reader', schema: CHANGES, label: 'reader', phase: 'Read' })

phase('Build')
const build = await agent(
  'Client: ' + client + '. Apply these requested changes to sites/' + client + '/index.html:\n' +
  JSON.stringify(req.changes, null, 2) +
  '\nThen run `python check-site.py ' + client + '` until it passes.',
  { agentType: 'builder', schema: BUILD, label: 'builder', phase: 'Build' })

phase('Critic')
const critic = await agent(
  'Client: ' + client + '. Check sites/' + client + '/index.html against data/' + client + '.json and give your verdict.',
  { agentType: 'critic', schema: VERDICT, label: 'critic', phase: 'Critic' })

phase('Report')
const reportPath = 'reports/' + client + '-site-refresh.md'
await agent(
  'Write the job report to ' + reportPath + '. Facts:\n' +
  JSON.stringify({ client, requested: req.changes, build, critic }, null, 2),
  { agentType: 'reporter', label: 'reporter', phase: 'Report' })

return { client, checker_passed: build.checker_passed, critic_verdict: critic.verdict,
         critic_mismatches: critic.mismatches, critic_note: critic.note, report: reportPath }
