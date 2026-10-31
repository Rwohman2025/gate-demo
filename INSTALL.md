# Set up `gate-demo` on any computer

This repository starts the Comprehension Gate directly from the public
Dartmouth GitHub repository. No personal `C:\Users\...` path is used.

## 1. Install the prerequisites

Install Git and [uv](https://docs.astral.sh/uv/). Then clone this repository:

```powershell
git clone https://github.com/Rwohman2025/gate-demo.git
cd gate-demo
```

Install the gate once. This downloads it from GitHub before Claude Code tries
to connect, avoiding a first-launch timeout:

```powershell
uv tool install --python 3.14 "git+https://github.com/Rwohman2025/Dartmouth.git@main#subdirectory=mcp-gate"
uv tool update-shell
```

Close and reopen your terminal and Claude Code after running these commands.
`uv tool update-shell` makes the installed `mcp-gate` command available to
Claude Code.

## 2. Set the two local environment variables

The gate needs the deployed backend address and the shared gate secret. Never
put the secret in this repository or commit it to Git.

On Windows PowerShell, run these commands once, replacing the second value
with the current secret from the project owner:

```powershell
setx BACKEND_URL "https://dartmouth-production.up.railway.app"
setx GATE_SECRET "paste-the-shared-secret-here"
```

Close and reopen Claude Code after using `setx`. On macOS or Linux, set the
same two variables in the terminal that launches Claude Code.

## 3. Use the gate

The `.mcp.json` file starts the already-installed `mcp-gate` command, so the
MCP connection opens immediately.

Ask Claude Code to create or change a file. It must call `propose_write`.
The gate stores the proposed file under `.pending/`, opens a question form,
and writes the real file only after the answer passes. If you cancel or fail
three attempts, the `.pending/` copy remains so you can review it.

Your MCP client must support elicitation forms for the question popup to
appear. Restart Claude Code if the `mcp-gate` tools do not show up.

To update the gate later, run this from any terminal:

```powershell
uv tool upgrade mcp-gate
```

## 4. Pull-request check

The GitHub Action in `.github/workflows/comprehension-check.yml` is already
configured. In the `gate-demo` GitHub repository, add these Actions secrets:

1. **Settings** > **Secrets and variables** > **Actions**.
2. Add `BACKEND_URL` with `https://dartmouth-production.up.railway.app`.
3. Add `GATE_SECRET` with the same shared secret used locally.

For protected merging into `main`, add **Comprehension Gate** as a required
status check in **Settings** > **Branches** > the `main` protection rule.
