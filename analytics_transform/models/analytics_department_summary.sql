{{ config(materialized='table') }}

SELECT 
    r.report_id,
    r.report_name,
    d.dept_name,
    SUM(d.budget) AS total_department_budget,
    COUNT(DISTINCT p.project_id) AS total_projects,
    COUNT(m.metric_name) AS total_metrics_recorded
FROM {{ source('main', 'main_report__departments') }} d
JOIN {{ source('main', 'main_report') }} r ON d._dlt_parent_id = r._dlt_id
LEFT JOIN {{ source('main', 'main_report__departments__projects') }} p ON p._dlt_parent_id = d._dlt_id
LEFT JOIN {{ source('main', 'main_report__departments__projects__metrics') }} m ON m._dlt_parent_id = p._dlt_id
GROUP BY 
    r.report_id,
    r.report_name,
    d.dept_name
