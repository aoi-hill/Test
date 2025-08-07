WITH crime_counts AS (
    SELECT 
        Location, 
        "Primary Type", 
        COUNT(ID) AS "Count Instances"
    FROM chicago
    GROUP BY Location, "Primary Type"
),
merged_data AS (
    SELECT 
        cc.Location, 
        cc."Primary Type", 
        cc."Count Instances",
        COALESCE(cr.Ranking, 999) AS Ranking
    FROM crime_counts cc
    LEFT JOIN crime_rank cr
        ON cc."Primary Type" = cr."Primary Type"
),
weighted_scores AS (
    SELECT 
        Location, 
        "Primary Type", 
        "Count Instances", 
        Ranking,
        1.0 / Ranking AS Weight,
        "Count Instances" * (1.0 / Ranking) AS "Weighted Crime Score"
    FROM merged_data
),
location_scores AS (
    SELECT 
        Location,
        SUM("Weighted Crime Score") AS "Total Weighted Score"
    FROM weighted_scores
    GROUP BY Location
),
ranked_locations AS (
    SELECT 
        ls.*,
        RANK() OVER (ORDER BY "Total Weighted Score" DESC) AS "Hotspot Rank"
    FROM location_scores ls
),
location_details AS (
    SELECT DISTINCT 
        UPPER(Block) AS Block, 
        Beat, 
        Location
    FROM chicago
)
SELECT 
    rl.Location, 
    ld.Block, 
    ld.Beat, 
    rl."Total Weighted Score", 
    rl."Hotspot Rank"
FROM ranked_locations rl
LEFT JOIN location_details ld
    ON rl.Location = ld.Location
ORDER BY "Hotspot Rank"
LIMIT 10;
