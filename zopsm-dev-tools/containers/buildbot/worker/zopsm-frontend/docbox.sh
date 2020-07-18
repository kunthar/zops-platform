#!/usr/bin/env sh

cp /buildbot/docbox_builder/build/docbox/dist/"$MD".md /buildbot/docbox_builder/build/docbox/content/"$MD".md
printf '%s\n' "
var fs = require('fs');
module.exports =
  '# ${MD}\n' +
  fs.readFileSync('./content/${MD}.md', 'utf8') + '\n';
" > /buildbot/docbox_builder/build/docbox/src/custom/content.js
cd /buildbot/docbox_builder/build/docbox
/usr/local/bin/npm run build
mkdir -p /buildbot/docbox_builder/build/dist/"$MD"
cp -r /buildbot/docbox_builder/build/docbox/* /buildbot/docbox_builder/build/dist/"$MD"
