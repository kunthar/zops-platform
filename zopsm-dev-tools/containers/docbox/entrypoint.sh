#!/usr/bin/env sh

cp /dist/"$MD".md /docbox/content/"$MD".md
printf '%s\n' "
var fs = require('fs');
module.exports =
  '# ${MD}\n' +
  fs.readFileSync('./content/${MD}.md', 'utf8') + '\n';
" > /docbox/src/custom/content.js
/usr/local/bin/npm run build
mkdir -p /dist/"$MD"
cp -r /docbox/* /dist/"$MD"