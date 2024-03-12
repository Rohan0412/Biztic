SELECT DISTINCT tie.num, tie.title, tie.portal_item_id
    FROM vonly_data_feed_us_staging.tv_ids tie
    INNER JOIN tv_id_mappings timi ON tie.id = timi.episode_vonly_id
    INNER JOIN tv_ids tisi ON tisi.id = timi.season_vonly_id
    WHERE tisi.platform NOT IN ('Amazon Movies & TV', 'WB MPM-VVId', 'YouTube', 'WB UPC')
	 	AND tie.scope = 'tv_season' 
      AND tie.vonly_asset_id IN (
										SELECT ti.vonly_asset_id 
										FROM vonly_data_feed_us_staging.tv_ids ti
										WHERE ti.platform='wb mpm-vvid' AND ti.scope='tv_season')
      ORDER BY CAST(tie.num AS SIGNED)