# Access and authentication

Three different things are easy to confuse. Keep them separate.

## 1. Reading this gateway
The repository is public. `git clone --depth 1 https://github.com/moamenessamseja-web/Flutter-Android-Build.git` needs no token. Single files can also be fetched from `https://raw.githubusercontent.com/moamenessamseja-web/Flutter-Android-Build/main/<path>`. An agent that cannot run git (read-only chat) can fetch `.agent/README.md` and the skill `SKILL.md` files that way, but it cannot run the scripts. For a harness with an authenticated HTTP tool but no shell or git, `HTTP_ONLY.md` gives the GitHub REST API equivalents of clone, commit, push, PR, build and report.
If the repository is ever made private, the agent token below needs read access to it too, and the repository setting *Settings -> Actions -> General -> Access* must allow other repositories to use its workflows.

## 2. Agent authentication (write access to target repositories)
The agent needs a GitHub token to push branches, open Pull Requests and dispatch workflows in the target repository.
- Recommended: a fine-grained personal access token limited to the target repositories with: Contents: read & write, Pull requests: read & write, Actions: read & write (dispatch and artifact download), Metadata: read. Administration/Secrets/Workflows-write only if the agent must edit files under `.github/workflows/`.
- **A GitHub Actions secret is not readable by an external agent.** The secret `AGENT_CLOUD_SONNET` stored in a repository's Actions secrets is only injected into workflow runs. For an agent running outside GitHub, the same token value must be provided by the agent platform itself (environment variable or secret store). This repository cannot verify which of the two the owner has configured.
- Use the token only through a transient header or environment variable, e.g. `git -c http.extraheader="Authorization: Basic $(printf 'x-access-token:%s' "$GH_TOKEN" | base64 -w0)" push origin <branch>` and `Authorization: Bearer $GH_TOKEN` for the REST API. Never put it in a URL, remote, file, commit, log or documentation.

## 3. Workflow execution permissions
These are independent of the agent token:
- The caller workflow's `GITHUB_TOKEN` only needs `contents: read` for the reusable workflow (the workflow declares exactly that).
- The caller template passes no secrets because the workflow uses none. If a caller uses `secrets: inherit` it forwards the **caller repository's** secrets only, never secrets stored in this central repository. When release signing is added, pass the keystore secrets by name (see the comment in `templates/build-apk.yml`).
- Events created with `GITHUB_TOKEN` do not start other workflows. A Pull Request opened by the agent's own token (a PAT) triggers `pull_request` workflows normally; one opened by a workflow using `GITHUB_TOKEN` would not. This is why the agent should use the PAT, not a workflow, to open PRs.
- Fork pull requests do not receive secrets and get a read-only token.

## 4. Practical notes
- The owner gives a token in the chat when work needs one. Use it only as a transient header; never write it into a file, a remote URL, a commit, a log or a document. A token that was pasted in a chat stays in that chat's log: if the owner wants to be safe, rotate it; do not nag more than once.
- Check the token's identity and scopes at the start (`GET /user`, header `x-oauth-scopes`); pushing workflow files needs the `workflow` scope on a classic token.
- Accidental actions happen on a phone (a merge by a child's tap): read the real state through the API before acting on assumptions.

## 5. Lockfile workflow write permission (D1b)
`.github/workflows/lockfile.yml` is the first reusable workflow needing `contents: write`. It is safe because:
- it refuses `refs/heads/main` before checkout;
- it runs only when manually dispatched on a feature branch;
- it writes only `pubspec.lock` in the requested working directory;
- it pushes to the same dispatched branch, never to another branch;
- the push uses `GITHUB_TOKEN`, which does not trigger other workflows (no CI loop).
After dispatch, re-read HEAD (the bot lock commit) before opening the PR, and set `EXPECT_SHA` accordingly when waiting for CI.
