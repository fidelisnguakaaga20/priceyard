-- Owner-operated metadata only in existing Supabase priceyard SQL Editor.
-- No customer records, password, secret, function body or settings change.
-- Run the whole script. Editor connection cannot prove pooler-hop TLS.
BEGIN READ ONLY;
SET LOCAL statement_timeout = '5s';
SET LOCAL lock_timeout = '1s';

SELECT current_setting('server_version_num')::integer AS server_version_num,
       current_database() AS database_name,
       (SELECT jsonb_agg(version_num ORDER BY version_num)
        FROM public.alembic_version) AS installed_revisions;

ROLLBACK;
