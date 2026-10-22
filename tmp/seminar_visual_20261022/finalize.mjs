import path from 'node:path';
import {pathToFileURL} from 'node:url';
process.env.RUNTIME_NODE_MODULES='/Users/kouta/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules';
process.env.RUNTIME_NODE='/Users/kouta/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node';
process.env.RUNTIME_PYTHON='/Users/kouta/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3';
process.env.RUNTIME_BIN_DIR='/Users/kouta/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/override';
const ROOT='/Users/kouta/Github/data augumation/Data-Augumation';
const S='/Users/kouta/.codex/plugins/cache/openai-primary-runtime/presentations/26.1020.11127/skills/presentations';
const D=ROOT+'/tmp/seminar_visual_20261022';
const {finalizePresentation}=await import(pathToFileURL(path.join(S,'container_tools/artifact_tool_utils.mjs')).href);
const r=await finalizePresentation({
 workspaceDir:ROOT,
 candidatePath:D+'/candidate.pptx',
 finalPath:ROOT+'/output/presentations/ゼミ_不均衡分類_20261022/不均衡分類_流れと図解を整えた発表版.pptx',
 pythonExecutable:process.env.RUNTIME_PYTHON,
 integrityValidatorPath:S+'/container_tools/inspect_presentation_package_integrity.py',
 layoutValidatorPath:S+'/container_tools/inspect_presentation_layout_geometry.py',
 layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit'],
 fontPolicy:{basis:'design',families:['Hiragino Sans']},
 requiredNativeChartOwnerSlides:[3,6,8,9,10,16,17,18],
 materializeLiteralChartWorkbooks:true,
 nativeChartTargetApplication:'powerpoint',
 verifyArtifactToolImport:true,
 receiptPath:D+'/validation.json'
});
console.log(JSON.stringify(r));
