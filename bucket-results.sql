CREATE TABLE chats (
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
        and s.status == 1  -- online
        and s.site_id = m.site_id
     ORDER BY s.timestamp DESC
     LIMIT 1) is null THEN 0 ELSE 1 END
     as chat
FROM messages m;

-- build an index on site_id
CREATE INDEX chats_site_id_idx ON chats(site_id, chat);

SELECT
  m.site_id AS site_id
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
ORDER BY m.site_id asc limit 10;


-- SELECT
--   m.site_id AS site_id
--    -- , COUNT(ch.chat)
--    -- , COUNT(email.chat)
--    , COUNT(m.from_id)
--    , COUNT(st.from_id)
-- FROM messages m
--      JOIN sites s
--           ON m.site_id = s.site_id
--      JOIN chats ch
--           ON s.site_id = ch.site_id
--      JOIN chats email
--           ON s.site_id = email.site_id
--      JOIN statuses st
--           on s.site_id = st.site_id
-- WHERE
--       ch.chat = 1
--       and email.chat = 0
-- GROUP BY m.site_id, m.from_id, st.from_id, ch.chat, email.chat
-- ORDER BY m.site_id asc
-- LIMIT 50;
