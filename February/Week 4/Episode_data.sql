Create VIEW [tv] AS 
SELECT ti.portal_item_id
FROM tv_ids AS ti
INNER JOIN sandbox.tvshows AS ts
ON ts.vonly_id = ti.id
WHERE ti.scope = 'tv_season' AND 
ti.platform NOT IN ("youtube","amazon movies & tv") 
ORDER BY ti.title ASC 
LIMIT 50
OFFSET 200;

SELECT 
   CONCAT('<table>',IFNULL (GROUP_CONCAT(DISTINCT CONCAT('<tr><td>',tie.num,'</td><td>', tie.title,'</td></tr>') order by CAST(tie.num AS SIGNED) SEPARATOR ' ' )," "),'</table>')
FROM 
   vonly_data_feed_us_staging.tv_ids tie
INNER JOIN 
   tv_id_mappings timi ON tie.id=timi.episode_vonly_id 
INNER JOIN 
   tv_ids tisi on tisi.id=timi.season_vonly_id
WHERE  
   tisi.id IN ( SELECT 
                   t.id 
               FROM 
                   tv_ids t 
               WHERE 
                   t.portal_item_id IN (SELECT * FROM [tv] ) 
					) 
AND tie.scope='tv_episode'  