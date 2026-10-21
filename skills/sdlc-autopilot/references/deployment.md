# Deployment preparation and recovery

Load only for deployment work. This reference authorizes no external mutation.
Honor an existing specific authorization; seek clarification only for a material
missing target, environment, action, or risk decision. Prepare the concrete change
and evidence before any final approval. A request to fix code alone is not a
request to deploy it. Preview authorization does not authorize production recovery.

## Prepare an exact operation

1. Inspect project instructions, CI, manifests, custom scripts, and nested commands.
   Config filenames suggest a platform; they do not identify the account or prove
   that a deploy script is safe. Do not run opaque custom scripts to discover effects.
2. Confirm CLI version/help and current official vendor guidance. Record account,
   organization, region, project/site/stack ID, environment, URL, revision/artifact
   digest, current healthy revision, and relevant database identity. Do not print secrets.
3. Use the platform's supported preview, plan/change set, or dry-run first. Review
   deletions, permission changes, migrations, traffic changes, and cost implications.
   If no preview is available, say so and use an isolated rehearsal when possible.
4. Define health/readiness checks, observation window, failure threshold, recovery
   target, and data compatibility. A successful CLI exit alone is insufficient.
5. Execute only the authorized exact operation. Use bounded retries for transient
   failures; stop on identity ambiguity, destructive surprises, or repeated failure.
6. On failure, inspect the actual affected environment. A failed preview must not
   trigger production rollback. Recovery is a separate scoped mutation unless it
   was explicitly included in the authorized incident/recovery plan. Validate the
   selected recovery revision and health after recovery.

## Platform distinctions

| Platform | What to verify before execution |
|---|---|
| Supabase | Link to the confirmed project identity, inspect migration history, and use the linked-project `db push` workflow with supported dry-run flags from installed help. `migration repair --status reverted` changes history only; it never reverts SQL or data. Reconcile history only after establishing actual schema state. Rehearse migrations and choose forward correction/restore/reversal deliberately. |
| Vercel | Confirm team/project and preview versus production. Promotion/instant rollback changes traffic identity and has environment/configuration implications. Select an exact previously healthy deployment and verify compatibility. |
| Netlify | Confirm account/site and deploy ID. Publishing a previous deploy does not automatically restore Netlify Database. Review code/data compatibility and current installed CLI help; do not assume a generic `rollback` command exists. |
| Docker / Compose | Confirm Docker context, Compose project, files, services, image digests, and volume/data ownership. Recover by selecting a known prior immutable image/configuration compatible with current data. Scope service replacement. A stopped container still owns its name; plan explicit scoped replacement or distinct candidate naming/traffic switching. |
| AWS / CloudFormation / SAM / Serverless | Confirm caller identity, account, region, stack, and template/artifact. Inspect a change set. Stack recovery commands depend on current stack state; `rollback-stack` is not a universal previous-version deployment. `delete-stack` destroys resources and is never routine rollback. |
| Git-triggered hosting | Verify the target branch and CI/hosting trigger before push. A Git update may deploy production. Avoid generic pull/rebase recipes in a checkout containing user work. |

Never use repository stashing, broad service shutdown, port-owner termination,
Docker system pruning, or unrelated cleanup as deployment error handling. Diagnose
port conflicts and report ownership; choose an alternate authorized port or a
scoped change. Do not run real deployments/migrations/recovery to test this skill;
use mocked CLIs or disposable isolated resources with no production credentials.

## Official references

Reviewed 2026-10-21; recheck the installed CLI and current vendor docs at execution.
These references support platform distinctions, not a universal executable recipe.

- [Supabase CLI: migration repair and linked push](https://supabase.com/docs/reference/cli/supabase-migration-repair)
- [Supabase database migrations](https://supabase.com/docs/guides/deployment/database-migrations)
- [Vercel promotion and recovery](https://vercel.com/docs/deployments/promoting-a-deployment)
- [Netlify previous deploy and database recovery](https://docs.netlify.com/build/data-and-storage/netlify-database/backup-and-recovery/)
- [Compose production configuration](https://docs.docker.com/compose/how-tos/production/)
- [CloudFormation rollback-stack](https://docs.aws.amazon.com/cli/latest/reference/cloudformation/rollback-stack.html)
