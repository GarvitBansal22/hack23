package org.catalyst.util;

import java.util.List;
import java.util.Map;

public class Constants {
    public static final String DEBEZIUM_TOAST = "__debezium_unavailable_value";
    public static List<String> NOTICE_DEPENDENT_COMM = List.of("email", "sms", "whatsapp");

    public static Map<String, List<String>> NOTICE_KEY_MAPPING = Map.of(
            "email", List.of("notice_links", "notice_type_map"),
            "sms", List.of("notice_links", "notice_type_map"),
            "whatsapp", List.of("notice_links", "notice_type_map")
    );
    public static Map<String, List<String>> MODULE_KEY_MAPPING = Map.of(
            "email", List.of("company_id"),
            "dtmf_ivr", List.of("company_id", "vendor"),
            "sms", List.of("company_id", "vendor"),
            "whatsapp", List.of("company_id", "vendor"),
            "call", List.of("company_id", "vendor_id")
    );

    public static Map<String, String> CREATED_MAPPING = Map.of(
            "email", "created",
            "dtmf_ivr", "created",
            "sms", "created",
            "whatsapp", "created",
            "call", "created"
    );
}