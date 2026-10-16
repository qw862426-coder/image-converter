// Prints the tool pages' JS translation tables as JSON for the page generator.
const fs = require('fs'), vm = require('vm'), path = require('path');
const root = path.join(__dirname, '..');
const ctx = {}; vm.createContext(ctx);
const files = { image: ['assets/i18n-image.js', 'I18N'], doc: ['document-to-pdf/i18n.js', 'DOC_I18N'], scan: ['scan/i18n.js', 'SCAN_I18N'], bg: ['remove-background/i18n.js', 'BG_I18N'] };
const out = {};
for (const [k, [f, name]] of Object.entries(files)) {
  vm.runInContext(fs.readFileSync(path.join(root, f), 'utf8') + `\n;this.__${k} = ${name};`, ctx);
  out[k] = ctx['__' + k];
}
process.stdout.write(JSON.stringify(out));
