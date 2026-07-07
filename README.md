daily-sql-practice/
├── README.md
│
├── campaign-channel-cid-spike-root-cause/
│   ├── README.md
│   ├── schema.md
│   ├── mock_data/
│   │   ├── generate_mock_events.py
│   │   ├── raw_events.csv
│   │   └── scenario_notes.md
│   ├── setup/
│   │   ├── 00_create_raw_events.sql
│   │   ├── 01_load_mock_data_postgresql.sql
│   │   ├── 02_create_staging_events.sql
│   │   ├── 03_create_dimensions.sql
│   │   ├── 04_create_fact_events.sql
│   │   └── 05_validate_setup.sql
│   │   
│   ├── postgresql/
│   │   ├── 01_extract_campaign_id_from_url_and_payload.sql
│   │   ├── 02_check_campaign_id_source_priority.sql
│   │   ├── 03_detect_campaign_channel_spike_by_day.sql
│   │   ├── 04_compare_channel_distribution_before_after_spike.sql
│   │   ├── 05_trace_first_campaign_id_touchpoint.sql
│   │   ├── 06_identify_sessions_with_conflicting_campaign_sources.sql
│   │   ├── 07_validate_campaign_processing_rule_output.sql
│   │   ├── 08_detect_unexpected_campaign_overwrite_cases.sql
│   │   ├── 09_rank_campaign_sources_by_spike_contribution.sql
│   │   └── 10_build_campaign_spike_root_cause_summary.sql
│   ├── bigquery/
│   │   ├── 01_extract_campaign_id_from_url_and_payload.sql
│   │   ├── 02_check_campaign_id_source_priority.sql
│   │   ├── 03_detect_campaign_channel_spike_by_day.sql
│   │   ├── 04_compare_channel_distribution_before_after_spike.sql
│   │   ├── 05_trace_first_campaign_id_touchpoint.sql
│   │   ├── 06_identify_sessions_with_conflicting_campaign_sources.sql
│   │   ├── 07_validate_campaign_processing_rule_output.sql
│   │   ├── 08_detect_unexpected_campaign_overwrite_cases.sql
│   │   ├── 09_rank_campaign_sources_by_spike_contribution.sql
│   │   └── 10_build_campaign_spike_root_cause_summary.sql
│   └── snowflake/
│       ├── 01_extract_campaign_id_from_url_and_payload.sql
│       ├── 02_check_campaign_id_source_priority.sql
│       ├── 03_detect_campaign_channel_spike_by_day.sql
│       ├── 04_compare_channel_distribution_before_after_spike.sql
│       ├── 05_trace_first_campaign_id_touchpoint.sql
│       ├── 06_identify_sessions_with_conflicting_campaign_sources.sql
│       ├── 07_validate_campaign_processing_rule_output.sql
│       ├── 08_detect_unexpected_campaign_overwrite_cases.sql
│       ├── 09_rank_campaign_sources_by_spike_contribution.sql
│       └── 10_build_campaign_spike_root_cause_summary.sql
│
├── deleted-button-still-firing-journey-trace/
│   ├── README.md
│   ├── postgresql/
│   │   ├── 01_find_deleted_button_event_occurrences.sql
│   │   ├── 02_check_event_volume_after_button_removal_date.sql
│   │   ├── 03_identify_pages_still_sending_deleted_button_event.sql
│   │   ├── 04_trace_previous_and_next_events_in_session.sql
│   │   ├── 05_detect_hidden_or_legacy_entry_points.sql
│   │   ├── 06_compare_event_source_by_platform_and_app_version.sql
│   │   ├── 07_find_duplicate_or_reused_tracking_names.sql
│   │   ├── 08_validate_event_against_current_ui_inventory.sql
│   │   ├── 09_classify_possible_source_type.sql
│   │   └── 10_build_deleted_button_root_cause_summary.sql
│   ├── bigquery/
│   │   ├── 01_find_deleted_button_event_occurrences.sql
│   │   ├── 02_check_event_volume_after_button_removal_date.sql
│   │   ├── 03_identify_pages_still_sending_deleted_button_event.sql
│   │   ├── 04_trace_previous_and_next_events_in_session.sql
│   │   ├── 05_detect_hidden_or_legacy_entry_points.sql
│   │   ├── 06_compare_event_source_by_platform_and_app_version.sql
│   │   ├── 07_find_duplicate_or_reused_tracking_names.sql
│   │   ├── 08_validate_event_against_current_ui_inventory.sql
│   │   ├── 09_classify_possible_source_type.sql
│   │   └── 10_build_deleted_button_root_cause_summary.sql
│   └── snowflake/
│       ├── 01_find_deleted_button_event_occurrences.sql
│       ├── 02_check_event_volume_after_button_removal_date.sql
│       ├── 03_identify_pages_still_sending_deleted_button_event.sql
│       ├── 04_trace_previous_and_next_events_in_session.sql
│       ├── 05_detect_hidden_or_legacy_entry_points.sql
│       ├── 06_compare_event_source_by_platform_and_app_version.sql
│       ├── 07_find_duplicate_or_reused_tracking_names.sql
│       ├── 08_validate_event_against_current_ui_inventory.sql
│       ├── 09_classify_possible_source_type.sql
│       └── 10_build_deleted_button_root_cause_summary.sql
│
├── bot-traffic-filtering-validation/
│   ├── README.md
│   ├── postgresql/
│   │   ├── 01_profile_traffic_by_user_agent.sql
│   │   ├── 02_detect_high_frequency_sessions.sql
│   │   ├── 03_identify_abnormal_event_velocity.sql
│   │   ├── 04_detect_repeated_payload_patterns.sql
│   │   ├── 05_compare_bot_like_vs_human_like_journeys.sql
│   │   ├── 06_validate_bot_filter_rule_coverage.sql
│   │   ├── 07_find_suspicious_ip_or_network_clusters.sql
│   │   ├── 08_measure_business_metric_impact_before_after_filter.sql
│   │   ├── 09_detect_false_positive_filtering_risk.sql
│   │   └── 10_build_bot_filtering_quality_summary.sql
│   ├── bigquery/
│   │   ├── 01_profile_traffic_by_user_agent.sql
│   │   ├── 02_detect_high_frequency_sessions.sql
│   │   ├── 03_identify_abnormal_event_velocity.sql
│   │   ├── 04_detect_repeated_payload_patterns.sql
│   │   ├── 05_compare_bot_like_vs_human_like_journeys.sql
│   │   ├── 06_validate_bot_filter_rule_coverage.sql
│   │   ├── 07_find_suspicious_ip_or_network_clusters.sql
│   │   ├── 08_measure_business_metric_impact_before_after_filter.sql
│   │   ├── 09_detect_false_positive_filtering_risk.sql
│   │   └── 10_build_bot_filtering_quality_summary.sql
│   └── snowflake/
│       ├── 01_profile_traffic_by_user_agent.sql
│       ├── 02_detect_high_frequency_sessions.sql
│       ├── 03_identify_abnormal_event_velocity.sql
│       ├── 04_detect_repeated_payload_patterns.sql
│       ├── 05_compare_bot_like_vs_human_like_journeys.sql
│       ├── 06_validate_bot_filter_rule_coverage.sql
│       ├── 07_find_suspicious_ip_or_network_clusters.sql
│       ├── 08_measure_business_metric_impact_before_after_filter.sql
│       ├── 09_detect_false_positive_filtering_risk.sql
│       └── 10_build_bot_filtering_quality_summary.sql
│
├── unencrypted-user-guid-collection/
│   ├── README.md
│   ├── postgresql/
│   │   ├── 01_detect_plaintext_user_identifier_pattern.sql
│   │   ├── 02_compare_raw_vs_processed_identifier_fields.sql
│   │   ├── 03_classify_identifier_encryption_status.sql
│   │   ├── 04_find_pages_collecting_plaintext_identifier.sql
│   │   ├── 05_find_events_collecting_plaintext_identifier.sql
│   │   ├── 06_detect_platform_or_version_specific_leakage.sql
│   │   ├── 07_trace_first_plaintext_identifier_occurrence.sql
│   │   ├── 08_measure_plaintext_identifier_exposure_rate.sql
│   │   ├── 09_validate_hash_format_consistency.sql
│   │   └── 10_build_identifier_security_audit_summary.sql
│   ├── bigquery/
│   │   ├── 01_detect_plaintext_user_identifier_pattern.sql
│   │   ├── 02_compare_raw_vs_processed_identifier_fields.sql
│   │   ├── 03_classify_identifier_encryption_status.sql
│   │   ├── 04_find_pages_collecting_plaintext_identifier.sql
│   │   ├── 05_find_events_collecting_plaintext_identifier.sql
│   │   ├── 06_detect_platform_or_version_specific_leakage.sql
│   │   ├── 07_trace_first_plaintext_identifier_occurrence.sql
│   │   ├── 08_measure_plaintext_identifier_exposure_rate.sql
│   │   ├── 09_validate_hash_format_consistency.sql
│   │   └── 10_build_identifier_security_audit_summary.sql
│   └── snowflake/
│       ├── 01_detect_plaintext_user_identifier_pattern.sql
│       ├── 02_compare_raw_vs_processed_identifier_fields.sql
│       ├── 03_classify_identifier_encryption_status.sql
│       ├── 04_find_pages_collecting_plaintext_identifier.sql
│       ├── 05_find_events_collecting_plaintext_identifier.sql
│       ├── 06_detect_platform_or_version_specific_leakage.sql
│       ├── 07_trace_first_plaintext_identifier_occurrence.sql
│       ├── 08_measure_plaintext_identifier_exposure_rate.sql
│       ├── 09_validate_hash_format_consistency.sql
│       └── 10_build_identifier_security_audit_summary.sql
│
├── missing-site-code-datastream-root-cause/
│   ├── README.md
│   ├── postgresql/
│   │   ├── 01_detect_missing_site_code_by_country.sql
│   │   ├── 02_compare_raw_payload_and_processed_site_code.sql
│   │   ├── 03_trace_site_code_preprocessing_steps.sql
│   │   ├── 04_validate_country_to_site_code_mapping.sql
│   │   ├── 05_check_datastream_id_distribution_by_country.sql
│   │   ├── 06_detect_mismatched_datastream_and_country.sql
│   │   ├── 07_compare_expected_vs_observed_datastream_mapping.sql
│   │   ├── 08_trace_first_breaking_point_in_pipeline.sql
│   │   ├── 09_measure_downstream_metric_impact_of_missing_site_code.sql
│   │   └── 10_build_site_code_root_cause_summary.sql
│   ├── bigquery/
│   │   ├── 01_detect_missing_site_code_by_country.sql
│   │   ├── 02_compare_raw_payload_and_processed_site_code.sql
│   │   ├── 03_trace_site_code_preprocessing_steps.sql
│   │   ├── 04_validate_country_to_site_code_mapping.sql
│   │   ├── 05_check_datastream_id_distribution_by_country.sql
│   │   ├── 06_detect_mismatched_datastream_and_country.sql
│   │   ├── 07_compare_expected_vs_observed_datastream_mapping.sql
│   │   ├── 08_trace_first_breaking_point_in_pipeline.sql
│   │   ├── 09_measure_downstream_metric_impact_of_missing_site_code.sql
│   │   └── 10_build_site_code_root_cause_summary.sql
│   └── snowflake/
│       ├── 01_detect_missing_site_code_by_country.sql
│       ├── 02_compare_raw_payload_and_processed_site_code.sql
│       ├── 03_trace_site_code_preprocessing_steps.sql
│       ├── 04_validate_country_to_site_code_mapping.sql
│       ├── 05_check_datastream_id_distribution_by_country.sql
│       ├── 06_detect_mismatched_datastream_and_country.sql
│       ├── 07_compare_expected_vs_observed_datastream_mapping.sql
│       ├── 08_trace_first_breaking_point_in_pipeline.sql
│       ├── 09_measure_downstream_metric_impact_of_missing_site_code.sql
│       └── 10_build_site_code_root_cause_summary.sql
│
├── user-agent-origin-platform-validation/
│   ├── README.md
│   ├── postgresql/
│   │   ├── 01_extract_user_agent_fields_from_payload.sql
│   │   ├── 02_detect_raw_platform_and_user_agent_mismatch.sql
│   │   ├── 03_validate_user_agent_based_overwrite_rule.sql
│   │   ├── 04_check_processed_platform_coverage.sql
│   │   ├── 05_compare_raw_vs_processed_platform_distribution.sql
│   │   ├── 06_detect_platform_overwrite_failures_by_page.sql
│   │   ├── 07_trace_platform_classification_by_session_journey.sql
│   │   ├── 08_identify_app_identifier_missing_or_malformed_cases.sql
│   │   ├── 09_measure_downstream_metric_impact_of_platform_misclassification.sql
│   │   └── 10_build_origin_platform_validation_summary.sql
│   ├── bigquery/
│   │   ├── 01_extract_user_agent_fields_from_payload.sql
│   │   ├── 02_detect_raw_platform_and_user_agent_mismatch.sql
│   │   ├── 03_validate_user_agent_based_overwrite_rule.sql
│   │   ├── 04_check_processed_platform_coverage.sql
│   │   ├── 05_compare_raw_vs_processed_platform_distribution.sql
│   │   ├── 06_detect_platform_overwrite_failures_by_page.sql
│   │   ├── 07_trace_platform_classification_by_session_journey.sql
│   │   ├── 08_identify_app_identifier_missing_or_malformed_cases.sql
│   │   ├── 09_measure_downstream_metric_impact_of_platform_misclassification.sql
│   │   └── 10_build_origin_platform_validation_summary.sql
│   └── snowflake/
│       ├── 01_extract_user_agent_fields_from_payload.sql
│       ├── 02_detect_raw_platform_and_user_agent_mismatch.sql
│       ├── 03_validate_user_agent_based_overwrite_rule.sql
│       ├── 04_check_processed_platform_coverage.sql
│       ├── 05_compare_raw_vs_processed_platform_distribution.sql
│       ├── 06_detect_platform_overwrite_failures_by_page.sql
│       ├── 07_trace_platform_classification_by_session_journey.sql
│       ├── 08_identify_app_identifier_missing_or_malformed_cases.sql
│       ├── 09_measure_downstream_metric_impact_of_platform_misclassification.sql
│       └── 10_build_origin_platform_validation_summary.sql
│
└── delivery-date-drift-tracking/
    ├── README.md
    ├── postgresql/
    │   ├── 01_check_missing_delivery_date_var_from_payload.sql
    │   ├── 02_check_delivery_date_var_page_coverage.sql
    │   ├── 03_check_delivery_date_var_cta_coverage.sql
    │   ├── 04_check_automatic_delivery_date_change_capture.sql
    │   ├── 05_check_delivery_date_format_validity.sql
    │   ├── 06_detect_edd_drift_by_session.sql
    │   ├── 07_trace_first_delivery_date_capture_in_journey.sql
    │   ├── 08_simulate_visit_level_dimension_persistence.sql
    │   ├── 09_measure_downstream_impact_of_missing_delivery_date.sql
    │   └── 10_build_delivery_date_drift_quality_summary.sql
    ├── bigquery/
    │   ├── 01_check_missing_delivery_date_var_from_payload.sql
    │   ├── 02_check_delivery_date_var_page_coverage.sql
    │   ├── 03_check_delivery_date_var_cta_coverage.sql
    │   ├── 04_check_automatic_delivery_date_change_capture.sql
    │   ├── 05_check_delivery_date_format_validity.sql
    │   ├── 06_detect_edd_drift_by_session.sql
    │   ├── 07_trace_first_delivery_date_capture_in_journey.sql
    │   ├── 08_simulate_visit_level_dimension_persistence.sql
    │   ├── 09_measure_downstream_impact_of_missing_delivery_date.sql
    │   └── 10_build_delivery_date_drift_quality_summary.sql
    └── snowflake/
        ├── 01_check_missing_delivery_date_var_from_payload.sql
        ├── 02_check_delivery_date_var_page_coverage.sql
        ├── 03_check_delivery_date_var_cta_coverage.sql
        ├── 04_check_automatic_delivery_date_change_capture.sql
        ├── 05_check_delivery_date_format_validity.sql
        ├── 06_detect_edd_drift_by_session.sql
        ├── 07_trace_first_delivery_date_capture_in_journey.sql
        ├── 08_simulate_visit_level_dimension_persistence.sql
        ├── 09_measure_downstream_impact_of_missing_delivery_date.sql
        └── 10_build_delivery_date_drift_quality_summary.sql