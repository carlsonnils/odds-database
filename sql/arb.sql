use sports_odds;

drop table if exists odds_temp;

create temporary table odds_temp
select * from odds;

drop table if exists arb1;

create temporary table arb1
select 
    o1.*,
    o2.book_key as book2,
    o2.last_update_book as last_update_book2,
    o2.team_name as team2,
    o2.price as price2
from odds_temp o1
join odds_temp o2 
on o1.game_id = o2.game_id
    and o1.sport_key = o2.sport_key
    and o1.book_key <> o2.book_key
    and o1.market_key = o2.market_key
    and o1.team_name <> o2.team_name;

drop table if exists arb;

create table arb
select * from arb1;
