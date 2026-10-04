# Report outline (fill each section from the files named in brackets)

1. **Introduction** - problem statement, objectives, dataset description (18 attributes, 5,000 students)
2. **Data warehouse design** - star schema diagram (draw: fact_placement in the middle, 5 dimensions around it),
   table descriptions, why bands are used [`sql/01_create_schema.sql`, row counts from step 01]
3. **OLAP analysis** - roll-up, drill-down, slice, dice, pivot with result tables and 1-2 line interpretations
   [`outputs/tables/olap_*.csv`]
4. **Pre-processing** - quality checks, outlier check, encoding, scaling, binning [`preprocessing_report.csv`]
5. **EDA** - class imbalance, correlation heatmap, rate by factor, box plots, salary distribution [`outputs/figures/eda_*`]
6. **Mining**
   - 6.1 Decision tree: features used, why salary was excluded, metrics, tree, rules, feature importance;
     note that perfect accuracy comes from rule-generated data
   - 6.2 K-means: elbow/silhouette, chosen K, cluster profile and names
   - 6.3 Apriori (optional): parameters, top rules by lift
7. **Tool simulation** - Power BI dashboard screenshots (+ WEKA J48 comparison if done) [`powerbi/`]
8. **Web scraping** (optional) - what was scraped, how it compares with dataset salaries
9. **Conclusion** - key factors (backlogs, CGPA, technical/soft skills), recommendations, limitations
   (synthetic-looking data, weak clusters, no time dimension)
10. **References**
