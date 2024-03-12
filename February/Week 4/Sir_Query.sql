SELECT * FROM vonly_data_feed_us_staging.tv_ids ti
WHERE  ti.scope='tv_season' AND ti.vonly_asset_id IN (
SELECT ti.vonly_asset_id FROM vonly_data_feed_us_staging.tv_ids ti
WHERE ti.platform='wb mpm-vvid' AND ti.scope='tv_season')