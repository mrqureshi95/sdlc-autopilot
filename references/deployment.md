# Deployment Reference

Loaded ONLY during deploy phase. Each section is self-contained.

## Detection Logic

Check in order. First match wins:
1. Custom deploy script: `package.json` scripts.deploy, `Makefile` deploy target, `deploy.sh`
2. `supabase/config.toml` → Supabase
3. `vercel.json` OR `.vercel/` → Vercel
4. `netlify.toml` OR `_redirects` → Netlify
5. `Dockerfile` OR `docker-compose.yml` OR `compose.yml` → Docker
6. `serverless.yml` OR `template.yaml` (SAM) → AWS
7. `.git/` with remote → Generic Git (push only)
No match → skip deploy, note in summary.

## Custom Deploy Script

**Detect:** `scripts.deploy` in package.json, `deploy:` in Makefile, or `deploy.sh` exists
**Deploy:** `npm run deploy` | `make deploy` | `chmod +x deploy.sh && ./deploy.sh`
**Rollback:** Check for `scripts.rollback` in package.json or `make rollback` target. If neither exists, note that manual rollback is required.
**Health:** Run `scripts.postdeploy` if defined, otherwise no automated health check.
**Failures:**
- Script not executable → `chmod +x deploy.sh`
- Missing env vars → check `.env.example` for required variables
- Exit code non-zero → capture stderr output, present to user, do NOT retry

## Supabase

**Detect:** `supabase/config.toml`
**Deploy functions:** `supabase functions deploy <name> --project-ref $SUPABASE_PROJECT_REF`
**Deploy migrations:** `supabase db push --project-ref $SUPABASE_PROJECT_REF`
**Deploy edge functions (all):** `supabase functions deploy --project-ref $SUPABASE_PROJECT_REF`
**Rollback functions:** Redeploy previous version from git history.
**Rollback migrations:** `supabase migration repair <version> --status reverted --project-ref $SUPABASE_PROJECT_REF`
**Health:** `curl -s https://$SUPABASE_PROJECT_REF.supabase.co/functions/v1/<name> -o /dev/null -w "%{http_code}"` — expect 200 or 401 (auth-protected).
**Failures:**
- Auth error → verify `SUPABASE_ACCESS_TOKEN` is set and valid
- Migration conflict → run `supabase db pull` first to sync remote state
- Function timeout → check bundle size, Deno import map
- "Project not found" → verify `SUPABASE_PROJECT_REF` matches dashboard

## Vercel

**Detect:** `vercel.json` or `.vercel/`
**Deploy preview:** `vercel --yes`
**Deploy prod:** `vercel --prod --yes` (only on explicit user request)
**Rollback:** `vercel rollback` — restores previous production deployment instantly.
**Health:** `curl -s $DEPLOYMENT_URL -o /dev/null -w "%{http_code}"` — expect 200. Preview URL printed in deploy output.
**Failures:**
- Not linked → `vercel link --yes`
- Build fails → check framework detection in `vercel.json`, verify env vars in dashboard
- Timeout → increase `maxDuration` in `vercel.json` (serverless functions)
- 404 on routes → check `rewrites` in `vercel.json` for SPA routing
- Rate limited → wait and retry after 60 seconds

## Netlify

**Detect:** `netlify.toml` or `_redirects`
**Build first:** Run build command from `netlify.toml` [build] section, or `npm run build`
**Deploy preview:** `netlify deploy --dir=<build-dir>`
**Deploy prod:** `netlify deploy --prod --dir=<build-dir>`
**Rollback:** `netlify rollback` or use dashboard to restore previous deploy. Each deploy is immutable.
**Health:** `curl -s $DEPLOY_URL -o /dev/null -w "%{http_code}"` — expect 200. Deploy URL printed in output.
**Failures:**
- Not linked → `netlify link`
- Wrong build dir → check `netlify.toml` `[build]` `publish` field
- Redirect loops → check `_redirects` or `[[redirects]]` in `netlify.toml`
- Functions fail → check `netlify/functions/` directory exists
- "Site not found" → verify site ID with `netlify status`

## AWS (Serverless / SAM)

**Detect:** `serverless.yml` or `template.yaml` (SAM)

### Serverless Framework
**Deploy:** `npx serverless deploy --stage $STAGE`
**Rollback:** `npx serverless rollback --timestamp <timestamp>` — restores to a previous CloudFormation stack state.
**List versions:** `npx serverless deploy list` — shows available rollback timestamps.
**Health:** Parse endpoint from deploy output, then `curl -s $API_ENDPOINT/health`

### AWS SAM
**Deploy:** `sam build && sam deploy --no-confirm-changeset --stack-name $STACK_NAME`
**Rollback:** `aws cloudformation rollback-stack --stack-name $STACK_NAME`
**Health:** `aws cloudformation describe-stacks --stack-name $STACK_NAME --query "Stacks[0].Outputs"` → extract endpoint → `curl -s $ENDPOINT/health`

**Failures (both):**
- Credentials → verify `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`
- Stack in ROLLBACK_COMPLETE → must delete stack first: `aws cloudformation delete-stack --stack-name $STACK_NAME`
- Stack in UPDATE_ROLLBACK_FAILED → `aws cloudformation continue-update-rollback --stack-name $STACK_NAME`
- Lambda too large → use layers or reduce dependencies
- Permission denied → check IAM role has required permissions
- Timeout during deploy → increase `--timeout` flag or check CloudFormation events for stuck resource

## Docker

**Detect:** `Dockerfile` or `docker-compose.yml` or `docker-compose.yaml` or `compose.yml` or `compose.yaml`

### Docker Compose (preferred if compose file exists)
**Detect compose file:** Check in order: `docker-compose.yml`, `docker-compose.yaml`, `compose.yml`, `compose.yaml`. Use whichever exists as `$COMPOSE_FILE`.
**Deploy:** `docker compose -f $COMPOSE_FILE up -d --build` (use `docker-compose` if `docker compose` not available)
**Rollback:** `docker compose -f $COMPOSE_FILE down && git stash && docker compose -f $COMPOSE_FILE up -d` — uses stash to avoid destructive checkout. Alternatively, redeploy the previous git tag/commit.
**Health:** `docker compose -f $COMPOSE_FILE ps` — all services should show "Up". Then: `docker inspect --format='{{.State.Health.Status}}' $CONTAINER` if HEALTHCHECK defined.

### Docker (standalone)
**Build:** `docker build -t $IMAGE_NAME:$TAG .`
**Push:** `docker push $IMAGE_NAME:$TAG`
**Run:** `docker run -d --name $CONTAINER -p $HOST_PORT:$CONTAINER_PORT $IMAGE_NAME:$TAG`
**Rollback:** `docker stop $CONTAINER && docker run -d --name $CONTAINER $IMAGE_NAME:$PREV_TAG`
**Health:** `docker inspect --format='{{.State.Health.Status}}' $CONTAINER` or `curl -s localhost:$HOST_PORT/health`

**Failures:**
- Port conflict → `docker ps` to find conflicting container, stop it
- Stale cache → rebuild with `docker build --no-cache -t $IMAGE_NAME:$TAG .`
- Disk full → `docker system prune -f` (removes dangling images/containers)
- Build fails → check Dockerfile syntax and base image availability
- Container exits immediately → `docker logs $CONTAINER` for error output

## Generic Git (Push Only)

**Detect:** `.git/` with remote, no other target matched
**Deploy:** `git push origin $(git branch --show-current)`
Note: This is NOT a deployment — just a push. Tell the user to deploy manually or set up CI/CD.
**Failures:**
- Rejected (non-fast-forward) → `git pull --rebase origin $(git branch --show-current)` then push
- No remote → `git remote add origin <url>` (ask user for URL)
- Auth failure → check SSH key or HTTPS token

## PR Creation

```bash
gh pr create --title "<conventional-commit-style title>" --body "<change summary from Phase 6>"
```
If `gh` not available → provide PR title and body for manual creation.
If PR already exists for branch → `gh pr view` to check, then update with `gh pr edit`.

## Conventional Commits

Format: `type(scope): description`
Types: `feat`, `fix`, `refactor`, `perf`, `test`, `docs`, `style`, `chore`, `ci`, `build`
Breaking changes: append `!` after type — `feat(api)!: remove deprecated endpoint`
Multi-line body: use `git commit` with heredoc for detailed description.

## General Deploy Rules

1. **Never deploy to production without explicit user approval.** Preview/staging deploys are acceptable.
2. **If deploy fails → attempt rollback** using the platform's rollback command above. If rollback also fails → capture both errors, present to user, do NOT retry.
3. **Always capture the deploy URL/ID** from output for the change summary.
4. **Environment variables:** Never include secret values in commands. Reference by name only (`$VAR_NAME`). If a required var is missing, tell the user which var to set.
5. **Post-deploy health check:** Run the platform's health check. If unhealthy → suggest rollback but do NOT auto-rollback without user approval.
