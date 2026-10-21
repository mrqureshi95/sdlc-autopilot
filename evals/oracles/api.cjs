// Evaluator-owned semantic checks. No deployment is performed.
const assert = require('node:assert/strict');
const { createRequire } = require('node:module');
const { join } = require('node:path');
const root = process.argv[2], kind = process.argv[3];
const completion = process.argv[4], nonce = process.argv[5];
const { writeFileSync } = require('node:fs');
function finish(state) {
  writeFileSync(completion,JSON.stringify({version:1,oracle:kind,nonce,state}),{flag:'wx'});
  process.exitCode={pass:0,fail:1,inconclusive:2}[state];
}
const req = createRequire(join(root, 'package.json'));
const request = req('supertest');
(async () => {
  const app = req(join(root, kind === 'health' ? 'src/server.js' : kind === 'sql' ? 'src/server.js' : 'src/app.js'));
  if (kind === 'health') {
    const res = await request(app).get('/health');
    assert.equal(res.status, 200);
    assert.equal(res.body.status, 'ok');
    assert.equal((await request(app).get('/api/data')).body.items.length,2);
  } else if (kind === 'validation' || kind === 'validation-strict') {
    for (const body of [{}, {text:null}, {text:42}, {text:[]}]) {
      const res = await request(app).post('/api/transform').send(body);
      assert.equal(res.status,400,JSON.stringify(body));
    }
    if (kind === 'validation-strict') for (const text of ['', '   ', 'x'.repeat(2001)]) {
      assert.equal((await request(app).post('/api/transform').send({text})).status,400);
    }
    const good=await request(app).post('/api/transform').send({text:'hello'});
    assert.equal(good.status,200); assert.equal(good.body.result,'HELLO');
  } else if (kind === 'sql') {
    for (const username of ["admin' OR '1'='1' --", "admin' --"]) {
      const res=await request(app).post('/auth/login').send({username,password:'wrong'});
      assert.equal(res.status,401);
      assert.equal(res.body.user,undefined);
    }
    assert.equal((await request(app).post('/auth/login').send({username:'admin',password:'wrong'})).status,401);
    const knownPassword = req(join(root,'src/db.js')).closeDb ? '$2b$10$hashedpassword' : 'hashed_pw';
    assert.equal((await request(app).post('/auth/login').send({username:'admin',password:knownPassword})).status,200);
    req(join(root,'src/db.js')).closeDb?.();
  } else throw Error('unknown oracle');
  finish('pass');
})().catch(e=>finish(e.code === 'ERR_ASSERTION' ? 'fail' : 'inconclusive'));
