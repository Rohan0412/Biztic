 SELECT ti.title AS title,case when  ti.num IS NULL then '' ELSE ti.num END  AS num ,ti.vonly_asset_id,   
        (
	 		SELECT GROUP_CONCAT(
                concat('<a target="_blank" rel="noopener" href=https://amazon.com/gp/video/detail/',ti_1.portal_item_id,'>',ti_1.portal_item_id,'</a>') 
                separator '<BR>'
			)
		    FROM tv_ids ti_1 
            WHERE ti_1.platform = 'amazon prime video' AND ti_1.vonly_asset_id = ti.vonly_asset_id
        ) AS amazon_ids,
        

        (
	 		SELECT GROUP_CONCAT(
		    	CONCAT('<a target="_blank" rel="noopener" href=https://www.vudu.com/content/browse/details/title/',ti_1.portal_item_id,'>',ti_1.portal_item_id, '</a>')
                SEPARATOR '<BR>'
            ) 
            FROM tv_ids ti_1 
            WHERE ti_1.platform = 'vudu' AND ti_1.vonly_asset_id = ti.vonly_asset_id
        ) AS vudu_ids,


        (
              SELECT GROUP_CONCAT(
                distinct CONCAT('<a target="_blank" rel="noopener" href=https://tv.apple.com/us/season/season/',ti_1.portal_item_id,'?showId=', ti_show.portal_item_id,' >', ti_1.portal_item_id, '</a>') 
                SEPARATOR '<BR>'
            ) 
            FROM tv_ids ti_1
			INNER JOIN tv_id_mappings tim ON ti_1.id=tim.season_vonly_id 
			INNER JOIN tv_ids ti_show ON tim.show_vonly_id= ti_show.id
            WHERE ti_1.platform = 'appletvapp' AND ti_1.vonly_asset_id = ti.vonly_asset_id AND ti_1.portal = 'AppleTV_CanonicalId'

        ) AS appletvapp_ids,


        (
            SELECT GROUP_CONCAT(
                concat('<a target="_blank" rel="noopener" href=https://itunes.apple.com/us/tv-season/title/id',ti_1.portal_item_id,'>',ti_1.portal_item_id,'</a>') 
                separator '<BR>'
            ) 
            FROM tv_ids ti_1 
            WHERE ti_1.platform = 'itunes' AND ti_1.vonly_asset_id = ti.vonly_asset_id
        ) AS itunes_ids,


        (
            SELECT GROUP_CONCAT(
                distinct concat('<a target="_blank" rel="noopener" href=https://play.google.com/store/tv/show/?id=',tsi.portal_item_id,'&hl=en_US&gl=US&cdid=tvseason-',ti_1.portal_item_id,'>',ti_1.portal_item_id,'</a>') 
                separator '<BR>'
            ) 
                FROM tv_ids ti_1 
                INNER JOIN tv_id_mappings tim ON ti_1.id=tim.season_vonly_id
                INNER JOIN tv_ids tsi ON tim.show_vonly_id=tsi.id
                WHERE ti_1.platform = 'google play' AND ti_1.vonly_asset_id = ti.vonly_asset_id AND ti_1.portal = 'google play'
        ) AS google_ids, 
        
        
        (
            SELECT GROUP_CONCAT(
                distinct CONCAT('<img src=''',case when ts_1.image_url is null then '' else ts_1.image_url end,''' height=150 width=150 alt=''', ts_1.portal_item_id, ''' />(', ts_1.distributed_by_parent, ')<BR>')
            ) 
            FROM tv_ids ti_1 
            LEFT OUTER JOIN sandbox.tvshows ts_1 ON ti_1.id = ts_1.vonly_id AND ti_1.region = ts_1.region
            WHERE ti_1.platform = 'amazon prime video' AND ti_1.vonly_asset_id = ti.vonly_asset_id
        ) AS amazon_urls, 


        (
            SELECT GROUP_CONCAT(
                CONCAT('<img src=''', CASE WHEN ts_1.image_url IS NULL THEN '' ELSE ts_1.image_url END, ''' height=150 width=150 alt=''', ts_1.portal_item_id, ''' />(', ts_1.distributed_by_parent, ')<BR>')
            )
            FROM tv_ids ti_1 
            LEFT OUTER JOIN sandbox.tvshows ts_1 ON ti_1.id = ts_1.vonly_id AND ti_1.region = ts_1.region
            WHERE ti_1.platform = 'vudu' AND ti_1.vonly_asset_id = ti.vonly_asset_id
        ) AS vudu_urls,


        (	                                                                                
            SELECT GROUP_CONCAT(
                DISTINCT CONCAT('<img src=''', CASE WHEN ts_1.image_url IS NULL THEN '' ELSE ts_1.image_url END, ''' height=150 width=150 alt=''', ts_1.portal_item_id, ''' />(', ts_1.distributed_by_parent,')<BR>')
            ) 
            FROM tv_ids ti_1 
            LEFT OUTER JOIN sandbox.tvshows ts_1 ON ti_1.id = ts_1.vonly_id AND ti_1.region = ts_1.region
            WHERE ti_1.platform = 'appletvapp' AND ti_1.vonly_asset_id = ti.vonly_asset_id and ti_1.portal = 'AppleTV_CanonicalId'
        ) AS appltvapp_urls,


        (                                                                             
            SELECT GROUP_CONCAT(
                CONCAT('<img src="',case when ts_1.image_url is null then '' else ts_1.image_url end ,'" height=150 width=150 alt=''',ts_1.portal_item_id,''' />(',ts_1.distributed_by_parent,')<BR>')
            ) 
            FROM tv_ids ti_1 
            LEFT OUTER JOIN sandbox.tvshows ts_1 ON ti_1.id = ts_1.vonly_id AND ti_1.region = ts_1.region
            WHERE ti_1.platform = 'itunes' AND ti_1.vonly_asset_id = ti.vonly_asset_id
        ) AS itunes_urls, 


        (                                                                             
            SELECT GROUP_CONCAT(
                DISTINCT CONCAT('<img src=''',case when ts_1.image_url is null then '' else ts_1.image_url end,''' height=150 width=150 alt=''',ts_1.portal_item_id,''' />(',ts_1.distributed_by_parent,')<BR>')
            ) 
            FROM tv_ids ti_1 
            LEFT OUTER JOIN sandbox.tvshows ts_1 ON ti_1.id = ts_1.vonly_id AND ti_1.region = ts_1.region
            WHERE ti_1.platform = 'google play' AND ti_1.vonly_asset_id = ti.vonly_asset_id 
        ) AS google_urls, 

        
        (
	 		SELECT GROUP_CONCAT(
                concat('<a target="_blank" rel="noopener" href=https://m.imdb.com/title/',im.portal_item_id,'>',im.portal_item_id,'</a>') 
                separator '<BR>'
			)
		    FROM sandbox.tv_imdb_ids im 
            WHERE im.vonly_asset_id = ti.vonly_asset_id
        ) AS imdb,


        (                                                                             
    	    SELECT GROUP_CONCAT(
	  			CONCAT('<img src=''',case when ts_1.image_url is null then '' else ts_1.image_url end,''' height=150 width=150 alt='')<BR>')
	        ) 
    		FROM sandbox.tvshows ts_1
			LEFT OUTER JOIN sandbox.tv_imdb_ids AS ii ON ts_1.vonly_asset_id=ii.vonly_asset_id
			WHERE ts_1.vonly_asset_id = ti.vonly_asset_id
        ) AS IMDB_urls 


    FROM tv_ids ti 
    LEFT OUTER JOIN sandbox.tvshows ts_1 ON ti.id = ts_1.vonly_id AND ti.region = ts_1.region
    WHERE ti.scope = 'tv_season' AND ti.platform = 'vudu'  ORDER BY 1 LIMIT 10;