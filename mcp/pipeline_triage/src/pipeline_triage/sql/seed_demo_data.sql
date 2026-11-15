-- Synthetic runs for two business days. 2026-11-15 has two failures with different
-- root causes (infrastructure vs. data contract); both pipelines succeeded the day before.
INSERT INTO pipeline_runs
    (run_id, pipeline_name, business_date, status, source_system, target_table, error_message, started_at)
VALUES
    (101, 'customer_master_daily', '2026-11-14', 'SUCCESS', 's3://demo/customer_raw',   'curated.customer_master', NULL,
          '2026-11-14 07:10:00+00'),
    (102, 'payments_ingest',       '2026-11-14', 'SUCCESS', 'kafka://demo/payments',    'bronze.payments',         NULL,
          '2026-11-14 07:15:00+00'),
    (103, 'inventory_sync',        '2026-11-14', 'FAILED',  'postgres://demo/inventory', 'curated.inventory',
          'Source connection timeout after 300s',
          '2026-11-14 06:30:00+00'),
    (201, 'orders_daily',          '2026-11-15', 'SUCCESS', 's3://demo/orders',         'curated.orders',          NULL,
          '2026-11-15 07:00:00+00'),
    (202, 'customer_master_daily', '2026-11-15', 'FAILED',  's3://demo/customer_raw',   'curated.customer_master',
          'Spark shuffle fetch failed: missing output location for shuffle 3',
          '2026-11-15 07:10:00+00'),
    (203, 'payments_ingest',       '2026-11-15', 'FAILED',  'kafka://demo/payments',    'bronze.payments',
          'Schema mismatch: column amount expected DECIMAL(18,2), received STRING',
          '2026-11-15 07:15:00+00'),
    (204, 'fx_rates_hourly',       '2026-11-15', 'SUCCESS', 'https://demo/fx-api',      'bronze.fx_rates',         NULL,
          '2026-11-15 08:00:00+00');
