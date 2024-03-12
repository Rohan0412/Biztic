CREATE VIEW tv AS
SELECT ti.title AS Season_Name, ti.num AS Season_Number, ti.platform, ti.portal_item_id, ts.description,
ts.produced_by_parent AS Studio,ts.actors, ts.genre , 
ts.us_theater_release_date AS RELEASE_Date, ts.producers,ts.writers,ts.director
FROM tv_ids AS ti
INNER JOIN sandbox.tvshows AS ts
ON ts.vonly_id = ti.id
WHERE ti.scope = 'tv_season' AND 
ti.platform NOT IN ('Amazon Movies & TV','WB MPM-VVId','YouTube','WB UPC')
ORDER BY ti.title ASC 
LIMIT 50
OFFSET 200;

SELECT portal_item_id FROM tv ;

SELECT CONCAT('<table>',IFNULL (GROUP_CONCAT(DISTINCT CONCAT('<tr><td>',tie.num,'</td><td>', tie.title,'</td><td>',tie.portal_item_id,'</td></tr>') order by CAST(tie.num AS SIGNED) SEPARATOR ' ' )," "),'</table>')

-- SELECT GROUP_CONCAT('<table>',CONCAT(tie.num ,tie.title , tie.portal_item_id),'</table>' SEPARATOR '<BR>')
FROM vonly_data_feed_us_staging.tv_ids tie
INNER JOIN tv_id_mappings timi ON tie.id = timi.episode_vonly_id
INNER JOIN tv_ids tisi ON tisi.id = timi.season_vonly_id
WHERE tisi.platform NOT IN ('Amazon Movies & TV', 'WB MPM-VVId', 'YouTube', 'WB UPC') 
  AND tisi.portal_item_id IN (SELECT portal_item_id FROM tv) 
  AND tie.scope = 'tv_episode'
GROUP BY tisi.portal_item_id;

