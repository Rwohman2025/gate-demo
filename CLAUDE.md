# Rules for this folder

All code must be saved with the `propose_write` tool (from the `mcp-gate` MCP server).

- To create or change any file, call `propose_write(file_path, content, task)`.
  Pass `file_path` as an absolute path and `content` as the complete new file.
- Do not use the Write, Edit or NotebookEdit tools. They are denied here.
- Do not write files through Bash (redirects, `tee`, `sed -i`, `cp`, scripts, etc.).
- If `propose_write` says the user has not shown understanding, stop. Do not
  retry it and do not write that file another way. Tell the user and let them decide.
