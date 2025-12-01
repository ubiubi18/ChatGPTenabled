# ChatGPTenabled: Vibe Coding Workflow

This repository documents a reproducible workflow for "vibe coding" with:

- ChatGPT (5.1 Thinking mode, plus Deep Research when needed)
- Codex (for direct code and file edits)
- GitHub as the project memory
- A local helper script `flatten_repo_to_md.py` that turns a repository into a single Markdown context file for ChatGPT

The core idea:

- You are the supervisor providing general guidance and direction.
- ChatGPT 5.1 Thinking is the assistant developer brain (reasoning, design, explanations).
- Codex is the hands (apply concrete edits to real files).
- GitHub is the long term memory (version control).
- `flatten_repo_to_md.py` is the camera that takes a snapshot of your repo and flattens it into one Markdown document you can feed to ChatGPT as context.
- At the end of each useful ChatGPT session, ChatGPT itself typically generates the Codex prompt that will apply its own proposed changes.

As an example, this workflow is used for a private project that combines Bitcoin regtest, Idena identity data, and a revived P2Pool fork (IdnaBTC_P2Pool_testnet). The same pattern works for any codebase.


## 1. Components of the workflow

### 1.1 ChatGPT (5.1 Thinking mode)

Use ChatGPT in 5.1 Thinking mode for:

- Understanding a codebase or a module
- Designing new features or refactors
- Reasoning about architecture and tradeoffs
- Generating code proposals and documentation drafts
- Explaining errors, logs, and complex edge cases
- Creating ready to use Codex prompts that apply its own suggested changes

This is the conversational "vibe coding" loop: you talk to ChatGPT like a pair programmer, it thinks with you, proposes solutions, and then prepares the exact Codex prompt to implement them.


### 1.2 ChatGPT Deep Research mode

Use Deep Research mode when you need:

- In depth web research
- Literature and standards research
- Surveys of existing tools and protocols
- Comparisons between technologies or libraries

Deep Research is for "what exists in the world" and "how do others solve this". 5.1 Thinking is for "how should we design and implement our version in this repo".


### 1.3 Codex

Use Codex as your editing assistant that actually modifies files. In this workflow:

- ChatGPT proposes changes (full files, functions, or diffs).
- ChatGPT then writes a Codex prompt for you that describes how to apply those changes.
- You copy this Codex prompt into Codex and run it in the repo root.
- Codex applies the changes to the real files in your local clone.

Typical Codex tasks:

- Apply a unified diff to a file
- Replace a function with a new implementation
- Create or update configuration files
- Update doc sections in `.md` files based on text from ChatGPT

You stay in full control of what is applied. ChatGPT prepares the Codex prompt, Codex executes it.


### 1.4 GitHub

GitHub is the canonical source of truth:

- All changes that Codex makes are committed here.
- Issues, branches, and pull requests still work as usual.
- You can use the same workflow for private and public repos.

You can treat ChatGPT and Codex as smart tools plugged into your normal Git workflow.


### 1.5 `flatten_repo_to_md.py`

The script `flatten_repo_to_md.py` turns a repository into a single Markdown file named `repo_context.md` that contains:

- A Markdown tree of the repository structure
- The contents of all allowed files (code and docs) in fenced code blocks

This file can be used as a "snapshot context" that you paste into ChatGPT so it can see the entire project at once.


### 1.6 Context windows, resets, and the wider model landscape (as of Nov 2025)

- Why resets matter: long chats accumulate drift, hidden assumptions, and forgotten constraints. Periodically starting a fresh chat (with a clean copy of `repo_context.md` or the relevant files) reduces hallucinations and keeps instructions sharp.
- Typical context window snapshots (approximate, forward-looking as of Nov 2025; always check current provider docs):
  - OpenAI: GPT-5.1 Thinking up to ~200k tokens; GPT-4.1 Turbo still common at 128k; smaller 16k-32k options remain for latency-sensitive tasks.
  - Anthropic: Claude 3.5/Opus family around 200k for general use, with larger 1M-token variants for heavy document runs.
  - Google: Gemini 1.5 Pro around 1M tokens; Nano/Flash tiers at smaller contexts for edge or low-latency paths.
  - Mistral & Llama ecosystem: Mistral Large 2 at ~128k; Llama 4/Next variants commonly tuned for 64k-128k; fine-tuned community checkpoints often cap at 32k-64k.
  - Others: Smaller OSS models (e.g., Phi/Sauerkraut variants) often sit at 8k-32k and require aggressive scoping.
- Modularize to fit windows: break vibe coding work into tightly scoped modules, keep per-chat payloads focused, and avoid pasting whole repos unless necessary. Use `flatten_repo_to_md.py` selectively (subtree slices) for large codebases.
- Discipline to reduce mistakes:
  - Define the task crisply (inputs, outputs, acceptance checks) before asking for code.
  - Keep diffs small and reviewable; ask for full-file rewrites only when needed.
  - Test and debug every step (unit tests, smoke checks, linters) to catch model slips early.
  - Watch for hallucinations: unexpected file deletions/renames, invented APIs, or silent logic changes often happen when instructions are vague or contexts are near limits.
  - When in doubt, reset the chat, restate constraints, and re-run a minimal example.
- Leadership and roadmap: a lead developer with a clear goal, test plan, and rollout sequence gives the model a safer lane. Ambiguous goals increase the chance of wandering context and incorrect edits.


## 2. Using `flatten_repo_to_md.py`

### 2.1 What the script does

- Walks the repository from a root directory.
- Skips common noise directories like `.git`, `node_modules`, `dist`, etc.
- Includes only files with certain extensions (code, config, docs).
- Renders a "Repository structure" section.
- Renders a "File contents" section with fenced code blocks and language hints.
- Writes the combined result to `repo_context.md` in the chosen root directory.

This gives you a single, self contained Markdown document you can feed into ChatGPT 5.1 Thinking mode.

### 2.2 How to run it

Clone or update your repo normally, then run the script locally.

Example:

```bash
# clone your repo or pull latest changes
git clone git@github.com:youruser/yourrepo.git
cd yourrepo

# copy flatten_repo_to_md.py into the repo root if it is not already there

# generate the Markdown snapshot
python flatten_repo_to_md.py

# you should now have:
# repo_context.md
```

You can also pass a custom root path:

```bash
python flatten_repo_to_md.py path/to/your/repo
```

After every bigger set of applied changes (for example, after a coding session where Codex updated multiple files), you can:

1. Pull the latest state from GitHub or use your local working copy.
2. Run `python flatten_repo_to_md.py` again.
3. Use the new `repo_context.md` as the context for your next ChatGPT session.

This keeps your ChatGPT context in sync with the real codebase.

### 2.3 What is included by default

The script includes files with these extensions:

- `.py`, `.js`, `.ts`, `.tsx`, `.jsx`
- `.go`, `.rs`, `.sol`
- `.md`, `.txt`
- `.json`, `.yml`, `.yaml`, `.toml`
- `.sh`, `.bash`
- `.html`, `.css`

Directories skipped by default:

- `.git`, `.idea`, `.vscode`
- `node_modules`, `dist`, `build`
- `__pycache__`

You can adjust these lists in the script if your stack is different.

## 3. Vibe coding workflow step by step

This is a reproducible pattern you can adapt.

### Step 0 - Prepare a context snapshot

- Update your repo or ensure your local copy is current.
- Run `python flatten_repo_to_md.py` in the repo root.
- Open `repo_context.md` in an editor and keep it ready for copy paste.

You now have a single file that describes your project structure and code.
### Step 1 - Start a new ChatGPT session (5.1 Thinking)

In a new ChatGPT 5.1 Thinking chat:

- Briefly describe the project and your goal for this session in your own words (3 to 10 sentences).
- Paste the contents of `repo_context.md` (or a large subset if the file is very big).
- Ask ChatGPT to:
  - Summarize the project.
  - Identify the main components.
  - Suggest a short list of high impact tasks or improvements.

Example first prompt:

```
You are my pair programmer and architecture coach.

Goal for this session:
- Make the identity Merkle tree builder more robust and better documented.

I will paste a Markdown snapshot of the entire repository (repo_context.md).
Please:
1. Summarize what this project does.
2. List the core modules and their roles.
3. Suggest 5 high impact improvements or next steps.

Here is the repo_context.md snapshot:
[PASTE CONTENTS OF repo_context.md HERE]
```

### Step 2 - Pick a single focused task

From the list of suggested tasks or from your own priorities, choose one focus:

- Improve a specific module.
- Implement a feature.
- Fix a bug.
- Clean up a config or pipeline.
- Update documentation.

Keep one session block focused on one main unit: one file, one feature, or one doc section.

### Step 3 - Ask ChatGPT to think before coding

For the file or feature you are working on:

- Paste only the relevant file or a smaller code section (not always the whole `repo_context.md` again).
- Ask ChatGPT for:
  - A short summary of what the code does.
  - A list of potential problems or missing cases.
  - A small plan in 3 to 5 steps.

Example:

```text
Task:
- Analyze and improve this file.

Please:
1. Summarize in a few sentences what it does.
2. List potential problems or edge cases.
3. Suggest a small change plan with 3 - 5 steps.

File: src/merkle/build_identity_merkle_tree.py
```

```python
[PASTE FILE CONTENT HERE]
```

Once the plan looks good, ask for concrete code.


### Step 4 - Ask ChatGPT for copy paste friendly code

You can either ask for a full replacement file or for a smaller diff.

Full file example:

```text
Now implement your plan and give me the complete updated file that I can copy paste into the repo.

Requirements:
- Keep the public API compatible if possible.
- Use short English comments where it improves readability.

File: src/merkle/build_identity_merkle_tree.py
```

Diff example:

```text
Now give me a unified diff against the current version.
```

Format:

```diff
@@ ...
- old line
+ new line
```

Only include changed parts.



### Step 5 - Let ChatGPT generate the Codex prompt

Instead of manually writing the Codex prompt yourself, you can let ChatGPT 5.1 Thinking generate it.

Typical pattern:

1. After ChatGPT has proposed the code or diff, you ask:

```text
Now please write a Codex prompt that will apply your suggested changes.

Requirements:
- Assume Codex runs in the repo root.
- The prompt should create or update exactly the affected file(s).
- It should not modify any unrelated files.
- It should include the new file content or diff inline.

ChatGPT responds with something like:

You are editing the repository "yourrepo".

1) Create or overwrite a file named src/merkle/build_identity_merkle_tree.py with the following content:

```python
[NEW CODE HERE]
```

Do not modify any other files.
```

3. You copy this Codex prompt and paste it into Codex while your working directory is the repo root.
4. Codex applies the changes exactly as described.

This way, ChatGPT not only designs the change but also prepares the exact Codex instructions to implement it. You remain in control and can review both the code and the Codex prompt before execution.


### Step 6 - Run and inspect locally

Run your usual commands in your shell, for example:

```bash
pytest
python scripts/run_lab.py
bitcoin-cli -regtest getblockcount
curl http://localhost:port/health
```

If something fails, bring back:

- The command you ran.
- The error output or traceback.
- The relevant code snippet.

and ask ChatGPT to help debug:

I applied your changes and got this error when running:

```bash
[command]
[error output]
```

Relevant code:

[function or block]

Please:

- Explain what is going wrong.
- Suggest a minimal fix.
- Provide the updated version of the affected function.



### Step 7 - Update documentation

When the code for this block is stable, update the docs so future you and collaborators understand the new state.

- Show ChatGPT the relevant doc section.
- Describe what changed.
- Ask it to rewrite the section.

Example:

```text
We changed how identity Merkle trees are built.

Here is the current section in docs/pipeline.md:

```markdown
[OLD SECTION]

Please rewrite this section to match the new implementation.
Keep it concise and practical. Output only the new section.

```

```


Apply the revised doc text via Codex and commit.


### Step 8 - Refresh `repo_context.md` periodically

After a set of changes:

1. Commit and push your work.
2. Re run `python flatten_repo_to_md.py`.
3. Use the new `repo_context.md` for the next bigger ChatGPT planning session.

This keeps ChatGPT's mental map aligned with your real repo.


## 4. When to use which OpenAI capability

### 4.1 ChatGPT 5.1 Thinking

Use 5.1 Thinking mode when:

- You need deep reasoning about your code and architecture.
- You want to discuss tradeoffs and design options.
- You want ChatGPT to keep a lot of context in working memory.
- You are doing step by step "vibe coding" in a chat window.
- You want ChatGPT to also generate Codex prompts that apply its suggested changes.

This is the main mode for this workflow.


### 4.2 Deep Research

Use Deep Research when:

- You need to look outward, beyond your repo.
- You want long form web research about protocols, standards, or best practices.
- You want comparisons between different approaches or tools in the ecosystem.

You can then bring the conclusions back into your 5.1 Thinking session and adapt them to your own codebase.


### 4.3 OpenAI API

Even if the owner of this repo prefers to work without the API, others might want to scale this pattern.

The API becomes useful when you want to:

- Automate `repo_context.md` generation and feeding into models.
- Build CLI tools that call ChatGPT or Codex as part of your normal workflows.
- Integrate coding suggestions into CI pipelines or bots.

The core ideas stay the same:

- Use models that are good at reasoning and planning for "thinking".
- Use models that are good at precise code editing for "doing".
- Use GitHub and your local shell for running, testing, and committing real changes.


## 5. Summary

This repository shows a human centric, conversational way to develop software:

- Flatten your repo into `repo_context.md` for a shared big picture.
- Use ChatGPT 5.1 Thinking as a pair programmer to understand, design, and plan.
- Let ChatGPT write ready to use Codex prompts that apply its own code suggestions.
- Use Codex to execute those prompts and edit your files safely.
- Commit everything to GitHub as usual.
- Optionally, use Deep Research for outward looking questions and the OpenAI API for automation.

It is not about fully autonomous agents, but about amplifying your own thinking and craft with AI tools while you keep control of the workflow.
