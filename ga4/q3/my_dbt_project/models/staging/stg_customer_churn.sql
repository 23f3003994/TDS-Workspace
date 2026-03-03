
-- ==========================================================
-- models/staging/stg_customer_churn.sql
--
-- MODEL 2: The Churn Analysis Model
-- Staging model: weekly churn rate analysis for last 30 days 
-- Uses {{ ref() }} to build on top of stg_customers
--
-- Job: Take the CLEAN data from stg_customers (Model 1)
--      and add churn-specific business logic:
--      - Flag which customers have churned
--      - Calculate which WEEK they churned (weekly granularity)
--      - Filter to last 30 days for recent trend analysis
--
-- Uses {{ ref('stg_customers') }} because it reads from Model 1
-- NOT from a raw table — so we use ref(), not source()
--
-- KEY RULE:
--   Raw table?        → use {{ source() }}
--   Another dbt model? → use {{ ref() }}
-- ==========================================================
with customers as (
-- ref() tells dbt to use the already-cleaned stg_customers model
 -- Rule: raw table → use source(), another dbt model → use ref()
    select * from {{ ref('stg_customers') }}

),

renamed as (

    select
        customer_id,
        email,
        signup_date,
        cancel_date,
        plan_type,
        monthly_revenue,

        -- flag: 1 = churned, 0 = still active
        case
            when cancel_date is not null then 1
            else 0
        end                                         as is_churned,

        -- week the customer churned e.g. "2024-W48"
        -- NULL if still active
        case
            when cancel_date is not null
            then strftime('%Y-W%W', cancel_date)
            else null
        end                                         as week_churned

    from customers

    -- last 30 days only: churned recently OR still active
    where
        (cancel_date >= date('now', '-30 days'))
        or cancel_date is null

)

select * from renamed
