CREATE TEMP TABLE chats (
  message_id TEXT NOT NULL
  , site_id TEXT NOT NULL
  , chat INTEGER NOT NULL
);

INSERT INTO chats(message_id, site_id, chat)
SELECT
  m.system_id
  , m.site_id
  , CASE WHEN
    ( SELECT s.timestamp
      FROM Statuses s
      WHERE s.timestamp <= m.timestamp
        and s.site_id = m.site_id
        and s.status == 1  -- online
     ORDER BY s.timestamp DESC
     LIMIT 1) is null THEN 0 ELSE 1 END
     as chat
FROM messages m;

SELECT
  m.site_id AS site_id
  , as chat
  , as email
  , (SELECT COUNT(*) FROM
      (SELECT distinct FROM_id
       FROM statuses st WHERE st.site_id = s.site_id))
  , (SELECT COUNT(*) FROM
       (SELECT DISTINCT FROM_id
        FROM messages ms WHERE ms.site_id = s.site_id))
FROM
        messages m JOIN sites s
                ON m.site_id = s.site_id
GROUP BY m.site_id
ORDER BY m.site_id asc;
