SELECT DISTINCT ti.title AS Season_Name, ti.num AS Season_Number,ti.vonly_asset_id, ti.platform, ti.portal_item_id, ts.description,
ts.produced_by_parent AS Studio,ts.actors, ts.genre , 
ts.us_theater_release_date AS RELEASE_Date, ts.producers,ts.writers,ts.director
FROM tv_ids AS ti
INNER JOIN sandbox.tvshows AS ts
ON ts.vonly_id = ti.id
WHERE ti.scope = 'tv_season' AND 
ti.platform NOT IN ('Amazon Movies & TV','WB MPM-VVId','YouTube','WB UPC')
ORDER BY ti.title ASC 
LIMIT 100
OFFSET 200

