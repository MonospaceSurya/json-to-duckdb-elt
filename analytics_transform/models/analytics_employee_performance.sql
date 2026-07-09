{{ config(materialized='table') }}

SELECT 
    r.report_id,
    r.report_name,
    d.dept_name,
    e.emp_id,
    e.name AS employee_name,
    e.is_manager,
    s.skill_name,
    s.level AS skill_level,
    pr.year AS review_year,
    pr.score AS review_score,
    pr.promoted
FROM {{ source('main', 'main_report__departments__employees__performance_reviews') }} pr
JOIN {{ source('main', 'main_report__departments__employees') }} e ON pr._dlt_parent_id = e._dlt_id
LEFT JOIN {{ source('main', 'main_report__departments__employees__skills') }} s ON s._dlt_parent_id = e._dlt_id
JOIN {{ source('main', 'main_report__departments') }} d ON e._dlt_parent_id = d._dlt_id
JOIN {{ source('main', 'main_report') }} r ON d._dlt_parent_id = r._dlt_id
