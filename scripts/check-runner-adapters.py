#!/usr/bin/env python3
"""Real pinned Jest/Vitest and JUnit-export integration controls. No installs."""
import argparse
import importlib.util
import json
from pathlib import Path
import tempfile
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('evidence',ROOT/'skills/sdlc-autopilot/scripts/evidence.py')
e=importlib.util.module_from_spec(spec);spec.loader.exec_module(e)
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--runtime-dir',type=Path,required=True);args=p.parse_args()
runtime=args.runtime_dir.resolve()
observations=[]
with tempfile.TemporaryDirectory(prefix='sdlc actual runners ') as temp:
    root=Path(temp).resolve()
    (root/'package.json').write_text('{"type":"module"}')
    vitest=runtime/'node_modules/vitest/vitest.mjs'
    jest=runtime/'node_modules/jest/bin/jest.js'
    (root/'node_modules').symlink_to(runtime/'node_modules',target_is_directory=True)
    (root/'vitest.config.mjs').write_text('import {defineConfig} from "vitest/config"; export default defineConfig({test:{globals:true}});')
    # Exercise the exact YAML-loading API affected by the narrow security override.
    (root/'.nycrc.yaml').write_text('all: true\nexclude:\n  - generated/**\n')
    yaml_control="const assert=require('node:assert/strict'); const {loadNycConfig}=require("+json.dumps(str(runtime/'node_modules/@istanbuljs/load-nyc-config'))+"); loadNycConfig({cwd:process.cwd()}).then(c=>{assert.equal(c.all,true);assert.deepEqual(c.exclude,['generated/**'])}).catch(()=>process.exit(1));"
    control=e.execute(['node','-e',yaml_control],root,30)
    if control['returncode'] or control.get('error'): raise SystemExit('Pinned YAML override compatibility failed')
    # Exercise the include/exclude and sync/async glob APIs after security overrides.
    (root/'src/excluded').mkdir(parents=True)
    (root/'src/included.js').write_text('module.exports = 4;\n')
    (root/'src/excluded/ignored.js').write_text('module.exports = 0;\n')
    exclude_control="""
const assert=require('node:assert/strict');
const path=require('node:path');
const TestExclude=require('test-exclude');
const filter=new TestExclude({cwd:process.cwd(),include:['src/**/*.js'],exclude:['src/excluded/**']});
assert.equal(filter.shouldInstrument(path.resolve('src/included.js')),true);
assert.equal(filter.shouldInstrument(path.resolve('src/excluded/ignored.js')),false);
const normalize=files=>files.map(file=>file.replaceAll('\\\\','/')).sort();
assert.deepEqual(normalize(filter.globSync()),['src/included.js']);
filter.glob().then(files=>assert.deepEqual(normalize(files),['src/included.js'])).catch(error=>{console.error(error);process.exitCode=1});
"""
    control=e.execute(['node','-e',exclude_control],root,30)
    if control['returncode'] or control.get('error'): raise SystemExit('Pinned glob/minimatch override compatibility failed: '+control.get('stderr',''))
    for runner,baseargv,filename in [
        ('jest-json',['node',str(jest),'--runInBand','--coverage','--config',json.dumps({'testMatch':['**/sample.test.cjs'],'collectCoverageFrom':['src/**/*.js']})],'sample.test.cjs'),
        ('vitest-json',['node',str(vitest)],'sample.test.js'),
        ('junit',['node',str(vitest),'run','--reporter=junit','--outputFile={report}'],'sample.test.js')]:
        for label,source,expected in [
            ('pass',"test('actual assertion',()=>{expect(2+2).toBe(4)});",'pass'),
            ('failure',"test('actual assertion',()=>{expect(2+2).toBe(5)});",'fail'),
            ('skip',"test.skip('not executed',()=>{expect(false).toBe(true)});",'inconclusive'),
            ('setup',"throw new Error('setup could not load');",'inconclusive')]:
            for prior in root.glob('sample.test.*'): prior.unlink()
            (root/filename).write_text(source)
            r=e.run_check({'name':'integration','kind':'test','runner':runner,'argv':baseargv},root,60)
            if label=='setup' and runner=='junit': expected='fail'
            observations.append({'runner':runner,'case':label,'expected':expected,'observed':r['state'],'count':r.get('count')})
            if r['state']!=expected:
                print(json.dumps({'controls':observations,'unexpected':r},indent=2));raise SystemExit(1)
print(json.dumps({'controls':observations,'matched':len(observations)},indent=2))
