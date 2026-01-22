---
description: Release a Loop agent version to letta-cloud
argument-hint: "<version> [letta-cloud-path]"
---

# Release Loop Agent v$1 to letta-cloud

Release the Loop agent file `loop-$1.af` to the letta-cloud repository.

## Parameters
- **Version**: $1
- **letta-cloud path**: $2 (defaults to `/Users/cameron/letta-cloud` if not provided)

## Source File
The agent file to release: `/Users/cameron/letta/loop/agentfiles/loop-$1.af`

## Release Steps

### 1. Verify source file exists
Check that `agentfiles/loop-$1.af` exists in this repository.

### 2. Create branch in letta-cloud
```bash
cd <letta-cloud-path>
git checkout main && git pull
git checkout -b cameron/loop-agent-v$1
```

### 3. Copy and update agent file
Copy the source file and replace version suffix:
```bash
cp /Users/cameron/letta/loop/agentfiles/loop-$1.af libs/config-agent-starter-kits/src/loop/loop.af
sed -i '' 's/Loop-$1/Loop/g' libs/config-agent-starter-kits/src/loop/loop.af
```

### 4. Generate initialAgent.ts
Convert the JSON to a TypeScript export:
```bash
cat libs/config-agent-starter-kits/src/loop/loop.af | node -e "
const fs = require('fs');
let json = '';
process.stdin.on('data', d => json += d);
process.stdin.on('end', () => {
  const data = JSON.parse(json);
  const ts = 'export const INITIAL_AGENT = ' + JSON.stringify(data, null, 2)
    .replace(/\"([^\"]+)\":/g, '\$1:')
    + ';\\n';
  console.log(ts);
});" > libs/service-auth/src/lib/findOrCreateUserAndOrganizationFromProviderLogin/initialAgent.ts
```

### 5. Commit and push
```bash
git add libs/config-agent-starter-kits/src/loop/loop.af \
        libs/service-auth/src/lib/findOrCreateUserAndOrganizationFromProviderLogin/initialAgent.ts
git commit --no-verify -m "feat: update Loop agent with v$1 improvements"
git push -u origin cameron/loop-agent-v$1
```

### 6. Create PR
```bash
gh pr create --title "feat: update Loop agent with v$1 improvements" --body "..."
```

## Key Notes
- The `initialAgent.ts` must stay in sync with `loop.af` - same data as TypeScript export
- `--no-verify` is acceptable for config-only changes (pre-commit hooks can be slow)
- PR body should summarize the changes from SPEC.md or loop_iterations memory
