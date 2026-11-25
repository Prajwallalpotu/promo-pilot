# Publishing promo-pilot

Maintainer: Prajwal Lalpotu · Repository: https://github.com/Prajwallalpotu/promo-pilot

Run every command from the project folder.

## First release

1. **Sign in to GitHub as the publishing account:** `gh auth status` must show `Prajwallalpotu`. If not, run `gh auth login`, or `gh auth switch -u Prajwallalpotu`.
2. **Keep your email private:** `git init`, then
   `git config user.email "$(gh api user --jq '"\(.id)+\(.login)@users.noreply.github.com"')"`
3. **Commit:** `git add . && git commit -m "promo-pilot 3.0.1"`
4. **Create the public repo and push:**
   `gh repo create promo-pilot --public --source=. --push --description "Professional promo videos from a link or a description, for Claude Code"`
5. **Release with the packaged skill:**
   `git tag v3.0.1 && git push --tags`, then
   `gh release create v3.0.1 dist/promo-pilot.skill --title "promo-pilot 3.0.1" --notes "First public release. See CHANGELOG.md."`
6. **Feedback label:** `gh label create feedback --description "Feedback from promo-pilot users" --color 0E8A16`
7. **Topics** (help people find it): `gh repo edit --add-topic claude-code,claude-skills,video,promo,hyperframes`

## How people install it

**As a plugin** (gets updates):
```
/plugin marketplace add Prajwallalpotu/promo-pilot
/plugin install promo-pilot@promo-pilot
```
**With the skills CLI:** `npx skills add https://github.com/Prajwallalpotu/promo-pilot -s promo-pilot -g -a claude-code -y`

**By copying** `skills/promo-pilot` into `~/.claude/skills/` (just for them) or into a project's `.claude/skills/` (for everyone working on that project).

Then `/promo-pilot setup` installs everything else in one step. It works in **local** Claude Code sessions (desktop app with a folder on the computer, terminal, IDE). Cloud sessions can't see personal skills and often block websites.

## Releasing updates

1. Edit the files. Your own install updates instantly, because `~/.claude/skills/promo-pilot` links to this folder.
2. Bump the version in `.claude-plugin/plugin.json`, `skills/promo-pilot/feedback_config.json` and `references/state.md`, and add a `CHANGELOG.md` entry.
3. Repackage `dist/promo-pilot.skill` (the skill-creator skill's `package_skill`).
4. `git commit -am "promo-pilot X.Y.Z" && git push`, then `git tag vX.Y.Z && git push --tags`, then `gh release create vX.Y.Z dist/promo-pilot.skill --notes "…"`.
5. Plugin users update with `/plugin marketplace update promo-pilot`.

## Before each release, check

- [ ] The tests in TESTING.md pass, and one real video was made with the new version.
- [ ] No API keys, personal paths, videos or test outputs are committed (`.gitignore` covers `promo-output*/`, `brag-output*/`, `dist/`, `evals/results/`).
- [ ] Public examples and demo videos use your own or invented businesses, not real big brands.

## Legal notes

- promo-pilot only *calls* the brag, hyperframes and media-use skills; it doesn't include their files. Users install them from their own repositories, under their own licenses.
- brag's bundled music is **CC BY 4.0** and needs the credit line, which promo-pilot adds to `share-copy.txt`.
- Don't use other companies' names or logos in your listing or examples in a way that suggests they endorse the skill.
