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
