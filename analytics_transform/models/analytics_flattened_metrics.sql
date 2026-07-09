{{ config(materialized='table') }}

SELECT 
    r.report_id,
    r.report_name,
    r.metadata__generated_by AS generated_by,
    r.metadata__is_audited AS is_audited,
    r.metadata__risk_score AS risk_score,
    r.company_details__name AS company_name,
    r.company_details__location AS company_hq,
    d.dept_name,
    d.budget AS department_budget,
    p.project_id,
    p.status AS project_status,
    m.metric_name,
    m.value AS metric_value
FROM {{ source('main', 'main_report__departments__projects__metrics') }} m
JOIN {{ source('main', 'main_report__departments__projects') }} p ON m._dlt_parent_id = p._dlt_id
JOIN {{ source('main', 'main_report__departments') }} d ON p._dlt_parent_id = d._dlt_id
JOIN {{ source('main', 'main_report') }} r ON d._dlt_parent_id = r._dlt_id
