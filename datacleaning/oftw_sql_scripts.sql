--------------- Total Active Donors 2025 -----------------

with a as (

        select case 
        	when date_part('month', cast(pledge_starts_at as date)) >= 7 then date_part('year', cast(pledge_starts_at as date)) + 1
        	else date_part('year', cast(pledge_starts_at as date))
        end as "Fiscal Year",

        case
        	when date_part('month', cast(pledge_starts_at as date)) >= 7 then date_part('month', cast(pledge_starts_at as date)) - 6
        	else date_part('month', cast(pledge_starts_at as date)) + 6 
        end as "Fiscal Month",

        cast(pledge_starts_at as date),
        pledge_status, 
        case when pledge_status = 'One-Time' then 'One-Time' else 'Subscription' end as "Pledge Type",
        pledge_id,
        donor_id

        from oftw.public.oftw_pledges_raw opr 
        where pledge_status not in ('ERROR', 'Payment failure')
        and date_part('year', cast(pledge_starts_at as date)) >= 2015

        )

        select cast(COUNT(distinct donor_id) as real) as "Number of Donors"
        from a
        where (pledge_status in ('Active donor', 'One-Time'))









------- Total Active Pledges 2025 ---------

with a as (

        select case 
        	when date_part('month', cast(pledge_starts_at as date)) >= 7 then date_part('year', cast(pledge_starts_at as date)) + 1
        	else date_part('year', cast(pledge_starts_at as date))
        end as "Fiscal Year",

        case
        	when date_part('month', cast(pledge_starts_at as date)) >= 7 then date_part('month', cast(pledge_starts_at as date)) - 6
        	else date_part('month', cast(pledge_starts_at as date)) + 6 
        end as "Fiscal Month",

        cast(pledge_starts_at as date),
        pledge_status, 
        case when pledge_status = 'One-Time' then 'One-Time' else 'Subscription' end as "Pledge Type",
        pledge_id,
        donor_id

        from oftw.public.oftw_pledges_raw opr 
        where pledge_status not in ('ERROR', 'Payment failure')
        and date_part('year', cast(pledge_starts_at as date)) >= 2015

        )

        select cast(COUNT(distinct pledge_id) as real) as "Number of Pledges"
        from a
        where (pledge_status in ('Active donor'))






---- Pledge Attrition Rate ----
with years as (select distinct date_part('year', cast(pledge_starts_at as date)) "fiscal_year" 
from oftw.public.oftw_pledges_raw 
where cast(pledge_starts_at as date) >= cast('2018-01-01' as date)
),

years_adjusted as (
select "fiscal_year",
CONCAT(cast("fiscal_year" - 1 as varchar(4)), '-07-01') as "fiscal_year_start",
CONCAT(cast("fiscal_year" as varchar(4)), '-06-30') as "fiscal_year_end"
from years),

active_pledges as (
select pledge_id, pledge_starts_at, pledge_status
from public.oftw_pledges_raw
where pledge_status in ('Active donor')),

churned_pledges as (

select pledge_id, pledge_starts_at , pledge_ended_at, pledge_status 
from public.oftw_pledges_raw
where (pledge_ended_at is not null and pledge_ended_at != '')
and pledge_status in ('Churned donor', 'Payment failure')

),

added_pledges as (

select pledge_id, pledge_starts_at , pledge_ended_at, pledge_status 
from public.oftw_pledges_raw
where (pledge_starts_at is not null and pledge_ended_at != '')
and pledge_status in ('Churned donor', 'Payment failure', 'Active donor')

)

,adds as (
select ya."fiscal_year", ya."fiscal_year_start", ya."fiscal_year_end",
cast(COUNT(distinct ap2.pledge_id) as real) "Added Pledges"
from years_adjusted ya
left join added_pledges ap2
on (cast(ya.fiscal_year_start as date) <= cast(ap2.pledge_starts_at as date) and cast(ya.fiscal_year_end as date) >= cast(ap2.pledge_starts_at as date))
group by ya."fiscal_year", ya."fiscal_year_start", ya."fiscal_year_end")


,pre_churned_fy as (
select ya."fiscal_year", ya."fiscal_year_start", ya."fiscal_year_end",
cast(COUNT(distinct cp2.pledge_id) as real) "Pre Churned Pledges"
from years_adjusted ya
left join churned_pledges cp2
on (cast(ya.fiscal_year_start as date) >= cast(cp2.pledge_starts_at as date) and cast(ya.fiscal_year_start as date) <= cast(cp2.pledge_ended_at as date))
group by ya."fiscal_year", ya."fiscal_year_start", ya."fiscal_year_end")

,churned_fy as (
select ya."fiscal_year", ya."fiscal_year_start", ya."fiscal_year_end",
cast(COUNT(distinct cp.pledge_id) as real) "Churned Pledges"
from years_adjusted ya
left join churned_pledges cp
on (cast(ya.fiscal_year_start as date) <= cast(cp.pledge_ended_at as date) and cast(ya.fiscal_year_end as date) >= cast(cp.pledge_ended_at as date))
group by ya."fiscal_year", ya."fiscal_year_start", ya."fiscal_year_end")

,active_fy as (
select ya."fiscal_year", ya."fiscal_year_start", ya."fiscal_year_end",
cast(COUNT(distinct ap.pledge_id) as real) "Active Pledges"
from years_adjusted ya
left join active_pledges ap
on (cast(ya.fiscal_year_start as date) >= cast(ap.pledge_starts_at as date))
group by ya."fiscal_year", ya."fiscal_year_start", ya."fiscal_year_end")

select a."fiscal_year", a."fiscal_year_start", a."fiscal_year_end", 
a."Active Pledges",
b."Churned Pledges",
c."Pre Churned Pledges",
d."Added Pledges"
from active_fy a
left join churned_fy b 
on a."fiscal_year" = b."fiscal_year"
left join pre_churned_fy c 
on a."fiscal_year" = c."fiscal_year"
left join adds d 
on a."fiscal_year" = d."fiscal_year"
order by a."fiscal_year" asc

-- View from query --
select * from 
public.oftw_churn_rate_fy
where "Fiscal Year" = 2025

--------------------------