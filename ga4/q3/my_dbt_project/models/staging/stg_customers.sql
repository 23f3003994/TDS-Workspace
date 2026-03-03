-- ==========================================================
-- models/staging/stg_customers.sql
--
-- MODEL 1: The Cleaning Model
--
-- Job: Take the raw messy table and clean it up.
--      - Rename bad column names to good ones
--      - Fix inconsistent text (MONTHLY → monthly)
--      - Handle NULL emails
--      - Cast text dates to real dates
--
-- Uses {{ source() }} because it reads from a RAW table
-- ==========================================================


-- CTE 1: source
-- Pull everything from the raw table
-- {{ source('raw_data', 'raw_customers') }} tells dbt:
--   "go find the source group called raw_data,
--    and inside it find the table called raw_customers"
with source as (

    select * from {{ source('raw_data', 'raw_customers') }}

),


-- CTE 2: renamed
-- Fix all the messy column names and data problems
renamed as (

    select

        -- Rename messy column names to clean readable names
        cust_id                                     as customer_id,

        -- Handle NULL emails: if email is missing, use a placeholder
        -- COALESCE means "use the first value that isn't NULL"
        coalesce(usr_email, 'unknown@example.com')  as email,

        -- Cast text dates to proper DATE format
        -- In SQLite, date() converts a text string "2024-01-10" to a real date
-- cast text dates to proper dates, NULL safe 
case
when signup_dt is not null then date(signup_dt) 
else null 
end as signup_date, 
case 
when cancel_dt is not null then date(cancel_dt) 
else null 
end as cancel_date,

        -- Fix inconsistent casing: monthly/MONTHLY/Monthly → monthly
        -- lower() makes everything lowercase
        lower(plan_typ)                             as plan_type,

        -- Rename mrr to a self-explanatory name
        mrr                                         as monthly_revenue

    from source

)


-- Final output: just return the cleaned data
select * from renamed
