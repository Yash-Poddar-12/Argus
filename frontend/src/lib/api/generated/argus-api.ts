// GENERATED from contracts/openapi/argus-api.yaml by scripts/generate-api.mjs. Do not edit.
export interface paths {
    "/health": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Health */
        get: operations["health_health_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/ready": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Ready */
        get: operations["ready_ready_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/version": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Version */
        get: operations["version_version_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/metrics": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Metrics Endpoint */
        get: operations["metrics_endpoint_metrics_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/auth/login": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Login */
        post: operations["login_api_v1_auth_login_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/auth/me": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Me */
        get: operations["me_api_v1_auth_me_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/sites/{site_id}/conditions": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Get Conditions */
        get: operations["get_conditions_api_v1_sites__site_id__conditions_get"];
        put?: never;
        /** Post Conditions */
        post: operations["post_conditions_api_v1_sites__site_id__conditions_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/sites": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** List Sites */
        get: operations["list_sites_api_v1_sites_get"];
        put?: never;
        /** Create Site */
        post: operations["create_site_api_v1_sites_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/sites/{site_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Get Site */
        get: operations["get_site_api_v1_sites__site_id__get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        /** Update Site */
        patch: operations["update_site_api_v1_sites__site_id__patch"];
        trace?: never;
    };
    "/api/v1/sites/{site_id}/zones": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** List Zones */
        get: operations["list_zones_api_v1_sites__site_id__zones_get"];
        put?: never;
        /** Create Zone */
        post: operations["create_zone_api_v1_sites__site_id__zones_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/sites/{site_id}/zones/{zone_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        /** Update Zone */
        patch: operations["update_zone_api_v1_sites__site_id__zones__zone_id__patch"];
        trace?: never;
    };
    "/api/v1/operators": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** List Operators */
        get: operations["list_operators_api_v1_operators_get"];
        put?: never;
        /** Create Operator */
        post: operations["create_operator_api_v1_operators_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/operators/{operator_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Get Operator */
        get: operations["get_operator_api_v1_operators__operator_id__get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        /** Update Operator */
        patch: operations["update_operator_api_v1_operators__operator_id__patch"];
        trace?: never;
    };
    "/api/v1/machines": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** List Machines */
        get: operations["list_machines_api_v1_machines_get"];
        put?: never;
        /** Create Machine */
        post: operations["create_machine_api_v1_machines_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/machines/{machine_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Get Machine */
        get: operations["get_machine_api_v1_machines__machine_id__get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        /** Update Machine */
        patch: operations["update_machine_api_v1_machines__machine_id__patch"];
        trace?: never;
    };
    "/api/v1/tasks": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Create Task */
        post: operations["create_task_api_v1_tasks_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/tasks/{task_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Get Task */
        get: operations["get_task_api_v1_tasks__task_id__get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        /** Update Task */
        patch: operations["update_task_api_v1_tasks__task_id__patch"];
        trace?: never;
    };
    "/api/v1/sites/{site_id}/tasks": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** List Site Tasks */
        get: operations["list_site_tasks_api_v1_sites__site_id__tasks_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/tasks/{task_id}/assign": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Assign Task */
        post: operations["assign_task_api_v1_tasks__task_id__assign_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/assignments": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Create Assignment */
        post: operations["create_assignment_api_v1_assignments_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/assignments/{assignment_id}": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        /** Patch Assignment */
        patch: operations["patch_assignment_api_v1_assignments__assignment_id__patch"];
        trace?: never;
    };
    "/api/v1/operators/{operator_id}/tasks/today": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Operator Tasks Today */
        get: operations["operator_tasks_today_api_v1_operators__operator_id__tasks_today_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/operators/{operator_id}/machine/confirm": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Confirm Machine */
        post: operations["confirm_machine_api_v1_operators__operator_id__machine_confirm_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/machines/{machine_id}/precheck": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Get Precheck */
        get: operations["get_precheck_api_v1_machines__machine_id__precheck_get"];
        put?: never;
        /** Post Precheck */
        post: operations["post_precheck_api_v1_machines__machine_id__precheck_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/tasks/{task_id}/start": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Start task */
        post: operations["start_task_api_v1_tasks__task_id__start_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/tasks/{task_id}/pause": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Pause task */
        post: operations["pause_task_api_v1_tasks__task_id__pause_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/tasks/{task_id}/resume": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Resume task */
        post: operations["resume_task_api_v1_tasks__task_id__resume_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/tasks/{task_id}/complete": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Complete task */
        post: operations["complete_task_api_v1_tasks__task_id__complete_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/tasks/{task_id}/summary": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Task Summary */
        get: operations["task_summary_api_v1_tasks__task_id__summary_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/telemetry": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Post Telemetry */
        post: operations["post_telemetry_api_v1_telemetry_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/machines/{machine_id}/telemetry": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Get Machine Telemetry */
        get: operations["get_machine_telemetry_api_v1_machines__machine_id__telemetry_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/operators/{operator_id}/twin": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Get Operator Twin */
        get: operations["get_operator_twin_api_v1_operators__operator_id__twin_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/sites/{site_id}/twin": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Get Site Twin */
        get: operations["get_site_twin_api_v1_sites__site_id__twin_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/v1/machines/{machine_id}/state": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Get Machine State */
        get: operations["get_machine_state_api_v1_machines__machine_id__state_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
}
export type webhooks = Record<string, never>;
export interface components {
    schemas: {
        /** AssignRequest */
        AssignRequest: {
            /** Operator Id */
            operator_id: string;
            /** Machine Id */
            machine_id: string;
            /**
             * Replace
             * @description Cancel the current active assignment and reassign
             * @default false
             */
            replace: boolean;
        };
        /** AssignmentCreate */
        AssignmentCreate: {
            /** Operator Id */
            operator_id: string;
            /** Machine Id */
            machine_id: string;
            /**
             * Replace
             * @description Cancel the current active assignment and reassign
             * @default false
             */
            replace: boolean;
            /** Task Id */
            task_id: string;
        };
        /** AssignmentDTO */
        AssignmentDTO: {
            /** Assignment Id */
            assignment_id: string;
            /** Task Id */
            task_id: string;
            /** Operator Id */
            operator_id: string;
            /** Machine Id */
            machine_id: string;
            /** Site Id */
            site_id: string;
            /** Assigned By */
            assigned_by: string;
            /**
             * Status
             * @enum {string}
             */
            status: "ACTIVE" | "CANCELLED" | "COMPLETED";
            /** Created At */
            created_at?: string | null;
        };
        /** AssignmentUpdate */
        AssignmentUpdate: {
            /** Status */
            status?: string | null;
            /** Machine Id */
            machine_id?: string | null;
        };
        /** AssistanceItem */
        AssistanceItem: {
            /**
             * Kind
             * @enum {string}
             */
            kind: "MACHINE" | "PERSON" | "RESOURCE" | "NOTE";
            /** Resource Id */
            resource_id?: string | null;
            /** Note */
            note?: string | null;
        };
        /** ConditionsUpdate */
        ConditionsUpdate: {
            conditions: components["schemas"]["EnvironmentConditions"];
            /** Zone Id */
            zone_id?: string | null;
            /**
             * Source
             * @default MANUAL
             */
            source: string;
        };
        /** ConfirmMachineRequest */
        ConfirmMachineRequest: {
            /** Machine Id */
            machine_id: string;
        };
        /** ConfirmMachineResponse */
        ConfirmMachineResponse: {
            /** Operator Id */
            operator_id: string;
            /** Machine Id */
            machine_id: string;
            /**
             * Confirmed At
             * Format: date-time
             */
            confirmed_at: string;
        };
        /** EnvironmentConditions */
        EnvironmentConditions: {
            /**
             * Weather
             * @default CLEAR
             * @enum {string}
             */
            weather: "CLEAR" | "CLOUDY" | "RAIN" | "STORM" | "FOG";
            /**
             * Temperature C
             * @default 30
             */
            temperature_c: number;
            /**
             * Rain Mm H
             * @default 0
             */
            rain_mm_h: number;
            /**
             * Visibility
             * @default GOOD
             * @enum {string}
             */
            visibility: "GOOD" | "MODERATE" | "POOR";
            /**
             * Soil
             * @default DRY
             * @enum {string}
             */
            soil: "DRY" | "WET" | "MUD" | "ROCKY";
        };
        /** GeoPoint */
        GeoPoint: {
            /** Lat */
            lat: number;
            /** Lon */
            lon: number;
        };
        /** HTTPValidationError */
        HTTPValidationError: {
            /** Detail */
            detail?: components["schemas"]["ValidationError"][];
        };
        /** IngestResult */
        IngestResult: {
            /** Received */
            received: number;
            /** Accepted */
            accepted: number;
            /** Duplicates */
            duplicates: number;
        };
        /** LoginRequest */
        LoginRequest: {
            /** Username */
            username: string;
            /** Password */
            password: string;
        };
        /** MachineCreate */
        MachineCreate: {
            /** Machine Id */
            machine_id: string;
            /** Site Id */
            site_id: string;
            /**
             * Machine Type
             * @enum {string}
             */
            machine_type: "EXCAVATOR" | "DUMPER" | "LOADER" | "DOZER" | "OTHER";
            /** Model */
            model: string;
            /** Serial Number */
            serial_number: string;
            /**
             * Engine Hours
             * @default 0
             */
            engine_hours: number;
        };
        /** MachineDTO */
        MachineDTO: {
            /** Machine Id */
            machine_id: string;
            /** Site Id */
            site_id: string;
            /**
             * Machine Type
             * @enum {string}
             */
            machine_type: "EXCAVATOR" | "DUMPER" | "LOADER" | "DOZER" | "OTHER";
            /** Model */
            model: string;
            /** Serial Number */
            serial_number: string;
            /**
             * Engine Hours
             * @default 0
             */
            engine_hours: number;
            /**
             * Status
             * @default ACTIVE
             * @enum {string}
             */
            status: "ACTIVE" | "INACTIVE" | "MAINTENANCE" | "RETIRED";
            /** Created At */
            created_at?: string | null;
        };
        /** MachineUpdate */
        MachineUpdate: {
            /** Site Id */
            site_id?: string | null;
            /** Model */
            model?: string | null;
            /** Engine Hours */
            engine_hours?: number | null;
            /** Status */
            status?: ("ACTIVE" | "INACTIVE" | "MAINTENANCE" | "RETIRED") | null;
        };
        /** MeResponse */
        MeResponse: {
            principal: components["schemas"]["Principal"];
            /** Permissions */
            permissions: string[];
        };
        /**
         * OperationalTwin
         * @description Human-Machine Operational Twin: state layer + intelligence layer (master §4).
         */
        OperationalTwin: {
            /** Operator Id */
            operator_id: string;
            /** Machine Id */
            machine_id?: string | null;
            /** Task Id */
            task_id?: string | null;
            /** Site Id */
            site_id: string;
            /**
             * As Of
             * Format: date-time
             */
            as_of: string;
            state: components["schemas"]["TwinState"];
            intelligence: components["schemas"]["TwinIntelligence"];
            freshness: components["schemas"]["TwinFreshness"];
        };
        /** OperatorCreate */
        OperatorCreate: {
            /** Operator Id */
            operator_id: string;
            /** Name */
            name: string;
            /** Site Id */
            site_id: string;
            /**
             * Experience Level
             * @default JUNIOR
             * @enum {string}
             */
            experience_level: "JUNIOR" | "INTERMEDIATE" | "SENIOR";
            /**
             * Certification Status
             * @default VALID
             * @enum {string}
             */
            certification_status: "VALID" | "EXPIRING" | "EXPIRED";
            /**
             * Preferred Language
             * @default en
             */
            preferred_language: string;
        };
        /** OperatorDTO */
        OperatorDTO: {
            /** Operator Id */
            operator_id: string;
            /** Name */
            name: string;
            /** Site Id */
            site_id: string;
            /**
             * Experience Level
             * @default JUNIOR
             * @enum {string}
             */
            experience_level: "JUNIOR" | "INTERMEDIATE" | "SENIOR";
            /**
             * Certification Status
             * @default VALID
             * @enum {string}
             */
            certification_status: "VALID" | "EXPIRING" | "EXPIRED";
            /**
             * Preferred Language
             * @default en
             */
            preferred_language: string;
            /**
             * Status
             * @default ACTIVE
             * @enum {string}
             */
            status: "ACTIVE" | "INACTIVE" | "MAINTENANCE" | "RETIRED";
            /** Created At */
            created_at?: string | null;
        };
        /** OperatorUpdate */
        OperatorUpdate: {
            /** Name */
            name?: string | null;
            /** Site Id */
            site_id?: string | null;
            /** Experience Level */
            experience_level?: ("JUNIOR" | "INTERMEDIATE" | "SENIOR") | null;
            /** Certification Status */
            certification_status?: ("VALID" | "EXPIRING" | "EXPIRED") | null;
            /** Preferred Language */
            preferred_language?: string | null;
            /** Status */
            status?: ("ACTIVE" | "INACTIVE" | "MAINTENANCE" | "RETIRED") | null;
        };
        /** Page[MachineDTO] */
        Page_MachineDTO_: {
            /** Items */
            items: components["schemas"]["MachineDTO"][];
            /** Total */
            total: number;
            /** Limit */
            limit: number;
            /** Offset */
            offset: number;
        };
        /** Page[OperatorDTO] */
        Page_OperatorDTO_: {
            /** Items */
            items: components["schemas"]["OperatorDTO"][];
            /** Total */
            total: number;
            /** Limit */
            limit: number;
            /** Offset */
            offset: number;
        };
        /** Page[SiteDTO] */
        Page_SiteDTO_: {
            /** Items */
            items: components["schemas"]["SiteDTO"][];
            /** Total */
            total: number;
            /** Limit */
            limit: number;
            /** Offset */
            offset: number;
        };
        /** PrecheckAnswer */
        PrecheckAnswer: {
            /** Item Id */
            item_id: string;
            /** Ok */
            ok: boolean;
            /** Note */
            note?: string | null;
        };
        /** PrecheckItem */
        PrecheckItem: {
            /** Item Id */
            item_id: string;
            /** Label */
            label: string;
            /**
             * Critical
             * @default false
             */
            critical: boolean;
        };
        /** PrecheckResultDTO */
        PrecheckResultDTO: {
            /** Precheck Id */
            precheck_id: string;
            /** Machine Id */
            machine_id: string;
            /** Operator Id */
            operator_id: string;
            /** Template Id */
            template_id: string;
            /** Passed */
            passed: boolean;
            /** Failed Items */
            failed_items: string[];
            /** Results */
            results: components["schemas"]["PrecheckAnswer"][];
            /**
             * Submitted At
             * Format: date-time
             */
            submitted_at: string;
        };
        /** PrecheckSubmit */
        PrecheckSubmit: {
            /** Results */
            results: components["schemas"]["PrecheckAnswer"][];
        };
        /** PrecheckTemplateDTO */
        PrecheckTemplateDTO: {
            /** Template Id */
            template_id: string;
            /** Machine Type */
            machine_type: string;
            /** Version */
            version: number;
            /** Items */
            items: components["schemas"]["PrecheckItem"][];
        };
        /** Principal */
        Principal: {
            /** User Id */
            user_id: string;
            /** Username */
            username: string;
            /**
             * Role
             * @enum {string}
             */
            role: "OPERATOR" | "SUPERVISOR_ADMIN";
            /** Operator Id */
            operator_id?: string | null;
            /**
             * Site Ids
             * @default []
             */
            site_ids: string[];
        };
        /** SessionDTO */
        SessionDTO: {
            /** Session Id */
            session_id: string;
            /** Task Id */
            task_id: string;
            /** Assignment Id */
            assignment_id: string;
            /** Operator Id */
            operator_id: string;
            /** Machine Id */
            machine_id: string;
            /**
             * Status
             * @enum {string}
             */
            status: "IN_PROGRESS" | "PAUSED" | "COMPLETED";
            /**
             * Actual Start
             * Format: date-time
             */
            actual_start: string;
            /** Actual End */
            actual_end?: string | null;
            /** Paused At */
            paused_at?: string | null;
            /**
             * Pause Duration S
             * @default 0
             */
            pause_duration_s: number;
            /** Start Load Cycles */
            start_load_cycles?: number | null;
        };
        /** SiteConditions */
        SiteConditions: {
            /** Site Id */
            site_id: string;
            site?: components["schemas"]["TwinEnvironment"] | null;
            /**
             * Zones
             * @default {}
             */
            zones: {
                [key: string]: components["schemas"]["TwinEnvironment"];
            };
            /** Environmental Difficulty */
            environmental_difficulty?: ("LOW" | "MEDIUM" | "HIGH") | null;
        };
        /** SiteCreate */
        SiteCreate: {
            /** Site Id */
            site_id: string;
            /** Name */
            name: string;
            location?: components["schemas"]["GeoPoint"] | null;
            /**
             * Timezone
             * @default UTC
             */
            timezone: string;
            /**
             * Configuration
             * @default {}
             */
            configuration: {
                [key: string]: unknown;
            };
        };
        /** SiteDTO */
        SiteDTO: {
            /** Site Id */
            site_id: string;
            /** Name */
            name: string;
            location?: components["schemas"]["GeoPoint"] | null;
            /**
             * Timezone
             * @default UTC
             */
            timezone: string;
            /**
             * Configuration
             * @default {}
             */
            configuration: {
                [key: string]: unknown;
            };
            /**
             * Status
             * @default ACTIVE
             * @enum {string}
             */
            status: "ACTIVE" | "INACTIVE" | "MAINTENANCE" | "RETIRED";
            /** Created At */
            created_at?: string | null;
        };
        /** SiteTwin */
        SiteTwin: {
            /** Site Id */
            site_id: string;
            /**
             * As Of
             * Format: date-time
             */
            as_of: string;
            /** Operators */
            operators: components["schemas"]["OperationalTwin"][];
            /** Machines */
            machines: components["schemas"]["TwinMachineState"][];
        };
        /** SiteUpdate */
        SiteUpdate: {
            /** Name */
            name?: string | null;
            location?: components["schemas"]["GeoPoint"] | null;
            /** Timezone */
            timezone?: string | null;
            /** Configuration */
            configuration?: {
                [key: string]: unknown;
            } | null;
            /** Status */
            status?: ("ACTIVE" | "INACTIVE" | "MAINTENANCE" | "RETIRED") | null;
        };
        /** TaskActionResponse */
        TaskActionResponse: {
            task: components["schemas"]["TaskDTO"];
            session: components["schemas"]["SessionDTO"];
        };
        /** TaskCreate */
        TaskCreate: {
            /**
             * Task Id
             * @description Optional; generated if omitted
             */
            task_id?: string | null;
            /** Site Id */
            site_id: string;
            /** Zone Id */
            zone_id?: string | null;
            /** Title */
            title: string;
            /**
             * Task Type
             * @enum {string}
             */
            task_type: "EXCAVATION" | "TRENCHING" | "LOADING" | "HAULING" | "GRADING" | "BACKFILLING" | "OTHER";
            /**
             * Priority
             * @default MEDIUM
             * @enum {string}
             */
            priority: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
            target: components["schemas"]["TaskTarget"];
            /**
             * Planned Start
             * Format: date-time
             */
            planned_start: string;
            /**
             * Planned End
             * Format: date-time
             */
            planned_end: string;
            /**
             * Assistance
             * @default []
             */
            assistance: components["schemas"]["AssistanceItem"][];
        };
        /** TaskDTO */
        TaskDTO: {
            /** Task Id */
            task_id: string;
            /** Site Id */
            site_id: string;
            /** Zone Id */
            zone_id?: string | null;
            /** Title */
            title: string;
            /**
             * Task Type
             * @enum {string}
             */
            task_type: "EXCAVATION" | "TRENCHING" | "LOADING" | "HAULING" | "GRADING" | "BACKFILLING" | "OTHER";
            /**
             * Priority
             * @enum {string}
             */
            priority: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
            target: components["schemas"]["TaskTarget"];
            /**
             * Planned Start
             * Format: date-time
             */
            planned_start: string;
            /**
             * Planned End
             * Format: date-time
             */
            planned_end: string;
            /**
             * Assistance
             * @default []
             */
            assistance: components["schemas"]["AssistanceItem"][];
            /**
             * Status
             * @enum {string}
             */
            status: "PLANNED" | "ASSIGNED" | "IN_PROGRESS" | "PAUSED" | "COMPLETED" | "CANCELLED";
            /** Created At */
            created_at?: string | null;
            /** Updated At */
            updated_at?: string | null;
        };
        /** TaskSummary */
        TaskSummary: {
            task: components["schemas"]["TaskDTO"];
            session?: components["schemas"]["SessionDTO"] | null;
            /** Planned Duration Min */
            planned_duration_min: number;
            /** Active Duration Min */
            active_duration_min?: number | null;
            /** Pause Duration Min */
            pause_duration_min?: number | null;
            /** Cycles Done */
            cycles_done?: number | null;
            /** Fuel Used Pct */
            fuel_used_pct?: number | null;
            /** Idle Min */
            idle_min?: number | null;
            /** Finished By Deadline */
            finished_by_deadline?: boolean | null;
        };
        /** TaskTarget */
        TaskTarget: {
            /**
             * Unit
             * @enum {string}
             */
            unit: "cycles" | "m3" | "tonnes" | "minutes";
            /** Value */
            value: number;
        };
        /** TaskUpdate */
        TaskUpdate: {
            /** Title */
            title?: string | null;
            /** Zone Id */
            zone_id?: string | null;
            /** Priority */
            priority?: ("LOW" | "MEDIUM" | "HIGH" | "CRITICAL") | null;
            target?: components["schemas"]["TaskTarget"] | null;
            /** Planned Start */
            planned_start?: string | null;
            /**
             * Planned End
             * @description The task deadline
             */
            planned_end?: string | null;
            /** Assistance */
            assistance?: components["schemas"]["AssistanceItem"][] | null;
            /**
             * Status
             * @description Only CANCELLED is accepted here; lifecycle uses the action endpoints
             */
            status?: ("PLANNED" | "ASSIGNED" | "IN_PROGRESS" | "PAUSED" | "COMPLETED" | "CANCELLED") | null;
        };
        /** TelemetryBatch */
        TelemetryBatch: {
            /** Items */
            items: components["schemas"]["TelemetryPoint"][];
        };
        /** TelemetryPoint */
        TelemetryPoint: {
            /** Machine Id */
            machine_id: string;
            /**
             * Ts
             * Format: date-time
             */
            ts: string;
            /** Engine Hours */
            engine_hours: number;
            /** Fuel Pct */
            fuel_pct: number;
            /** Fuel Rate Lph */
            fuel_rate_lph: number;
            /**
             * Load Cycles
             * @description Cumulative load-cycle counter
             */
            load_cycles: number;
            /**
             * Idle Seconds
             * @description Cumulative idle seconds counter
             */
            idle_seconds: number;
            /** Speed Kmh */
            speed_kmh: number;
            /** Rpm */
            rpm: number;
            /** Temperature C */
            temperature_c: number;
            /** Lat */
            lat: number;
            /** Lon */
            lon: number;
            /**
             * Operating Mode
             * @enum {string}
             */
            operating_mode: "DIGGING" | "SWINGING" | "DUMPING" | "LOADING" | "HAULING" | "RETURNING" | "TRAVELLING" | "IDLE" | "OFF";
            /** Seatbelt */
            seatbelt: boolean;
        };
        /** TodayTask */
        TodayTask: {
            task: components["schemas"]["TaskDTO"];
            assignment: components["schemas"]["AssignmentDTO"];
            session?: components["schemas"]["SessionDTO"] | null;
            /** Allowed Actions */
            allowed_actions: string[];
        };
        /** TokenResponse */
        TokenResponse: {
            /** Access Token */
            access_token: string;
            /**
             * Token Type
             * @default bearer
             */
            token_type: string;
            /** Expires In */
            expires_in: number;
            principal: components["schemas"]["Principal"];
        };
        /**
         * TwinEnvironment
         * @description Conditions as recorded for a site or zone (name kept for API compatibility).
         */
        TwinEnvironment: {
            /**
             * Weather
             * @default CLEAR
             * @enum {string}
             */
            weather: "CLEAR" | "CLOUDY" | "RAIN" | "STORM" | "FOG";
            /**
             * Temperature C
             * @default 30
             */
            temperature_c: number;
            /**
             * Rain Mm H
             * @default 0
             */
            rain_mm_h: number;
            /**
             * Visibility
             * @default GOOD
             * @enum {string}
             */
            visibility: "GOOD" | "MODERATE" | "POOR";
            /**
             * Soil
             * @default DRY
             * @enum {string}
             */
            soil: "DRY" | "WET" | "MUD" | "ROCKY";
            /** Zone Id */
            zone_id?: string | null;
            /** As Of */
            as_of?: string | null;
        };
        /** TwinFreshness */
        TwinFreshness: {
            /** Telemetry Age S */
            telemetry_age_s?: number | null;
            /** Environment Age S */
            environment_age_s?: number | null;
        };
        /**
         * TwinIntelligence
         * @description Slots filled by other capabilities' events. Nullable: the twin is valid without them.
         */
        TwinIntelligence: {
            /**
             * Safety
             * @description From safety.event.raised
             */
            safety?: {
                [key: string]: unknown;
            } | null;
            /**
             * Risk
             * @description From prediction.risk.updated (evidence only)
             */
            risk?: {
                [key: string]: unknown;
            } | null;
            /**
             * Eta
             * @description From prediction.task_time.updated
             */
            eta?: {
                [key: string]: unknown;
            } | null;
            /**
             * Anomaly
             * @description From operator.anomaly.detected
             */
            anomaly?: {
                [key: string]: unknown;
            } | null;
            /** Productivity */
            productivity?: {
                [key: string]: unknown;
            } | null;
            /** Environmental Difficulty */
            environmental_difficulty?: ("LOW" | "MEDIUM" | "HIGH") | null;
        };
        /** TwinMachineState */
        TwinMachineState: {
            /** Machine Id */
            machine_id: string;
            /** Machine Type */
            machine_type: string;
            /** Model */
            model: string;
            /** Telemetry At */
            telemetry_at?: string | null;
            /** Operating Mode */
            operating_mode?: ("DIGGING" | "SWINGING" | "DUMPING" | "LOADING" | "HAULING" | "RETURNING" | "TRAVELLING" | "IDLE" | "OFF") | null;
            /** Fuel Pct */
            fuel_pct?: number | null;
            /** Fuel Rate Lph */
            fuel_rate_lph?: number | null;
            /** Speed Kmh */
            speed_kmh?: number | null;
            /** Rpm */
            rpm?: number | null;
            /** Engine Hours */
            engine_hours?: number | null;
            /** Load Cycles */
            load_cycles?: number | null;
            /** Idle Seconds */
            idle_seconds?: number | null;
            /** Temperature C */
            temperature_c?: number | null;
            /** Seatbelt */
            seatbelt?: boolean | null;
            location?: components["schemas"]["GeoPoint"] | null;
            /** Health */
            health?: ("OK" | "WARNING" | "CRITICAL") | null;
        };
        /** TwinOperatorState */
        TwinOperatorState: {
            /** Name */
            name: string;
            /** Status */
            status: string;
            /** Experience Level */
            experience_level: string;
            /** Certification Status */
            certification_status: string;
            /**
             * Preferred Language
             * @default en
             */
            preferred_language: string;
            /** Machine Familiarity */
            machine_familiarity?: ("LOW" | "MEDIUM" | "HIGH") | null;
        };
        /** TwinSiteContext */
        TwinSiteContext: {
            /** Zone Id */
            zone_id?: string | null;
            /** Zone Type */
            zone_type?: string | null;
            /**
             * Active Machines
             * @default 0
             */
            active_machines: number;
            /**
             * Nearby Workers
             * @description Filled from the IoT hazard mesh; null until then
             */
            nearby_workers?: number | null;
            /**
             * Congestion
             * @description Filled from site operational intelligence; null until then
             */
            congestion?: ("LOW" | "MEDIUM" | "HIGH") | null;
        };
        /** TwinState */
        TwinState: {
            operator: components["schemas"]["TwinOperatorState"];
            machine?: components["schemas"]["TwinMachineState"] | null;
            task?: components["schemas"]["TwinTaskState"] | null;
            environment?: components["schemas"]["TwinEnvironment"] | null;
            site?: components["schemas"]["TwinSiteContext"] | null;
        };
        /** TwinTaskState */
        TwinTaskState: {
            /** Task Id */
            task_id: string;
            /** Title */
            title: string;
            /**
             * Task Type
             * @enum {string}
             */
            task_type: "EXCAVATION" | "TRENCHING" | "LOADING" | "HAULING" | "GRADING" | "BACKFILLING" | "OTHER";
            /**
             * Status
             * @enum {string}
             */
            status: "PLANNED" | "ASSIGNED" | "IN_PROGRESS" | "PAUSED" | "COMPLETED" | "CANCELLED";
            /** Zone Id */
            zone_id?: string | null;
            /**
             * Priority
             * @enum {string}
             */
            priority: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
            target: components["schemas"]["TaskTarget"];
            /** Cycles Done */
            cycles_done?: number | null;
            /** Progress Pct */
            progress_pct?: number | null;
            /**
             * Planned Start
             * Format: date-time
             */
            planned_start: string;
            /**
             * Planned End
             * Format: date-time
             */
            planned_end: string;
            /** Session Id */
            session_id?: string | null;
            /** Actual Start */
            actual_start?: string | null;
        };
        /** ValidationError */
        ValidationError: {
            /** Location */
            loc: (string | number)[];
            /** Message */
            msg: string;
            /** Error Type */
            type: string;
            /** Input */
            input?: unknown;
            /** Context */
            ctx?: Record<string, never>;
        };
        /** ZoneCreate */
        ZoneCreate: {
            /** Zone Id */
            zone_id: string;
            /** Name */
            name: string;
            /**
             * Zone Type
             * @enum {string}
             */
            zone_type: "TASK" | "HAZARD" | "RESTRICTED" | "DISPOSAL" | "SOFT_GROUND" | "OTHER";
            /**
             * Geometry
             * @description GeoJSON Polygon, coordinates [lon, lat]
             */
            geometry: {
                [key: string]: unknown;
            };
        };
        /** ZoneDTO */
        ZoneDTO: {
            /** Zone Id */
            zone_id: string;
            /** Site Id */
            site_id: string;
            /** Name */
            name: string;
            /**
             * Zone Type
             * @enum {string}
             */
            zone_type: "TASK" | "HAZARD" | "RESTRICTED" | "DISPOSAL" | "SOFT_GROUND" | "OTHER";
            /** Geometry */
            geometry: {
                [key: string]: unknown;
            };
            /**
             * Status
             * @default ACTIVE
             * @enum {string}
             */
            status: "ACTIVE" | "INACTIVE" | "MAINTENANCE" | "RETIRED";
        };
        /** ZoneUpdate */
        ZoneUpdate: {
            /** Name */
            name?: string | null;
            /** Zone Type */
            zone_type?: ("TASK" | "HAZARD" | "RESTRICTED" | "DISPOSAL" | "SOFT_GROUND" | "OTHER") | null;
            /** Geometry */
            geometry?: {
                [key: string]: unknown;
            } | null;
            /** Status */
            status?: ("ACTIVE" | "INACTIVE" | "MAINTENANCE" | "RETIRED") | null;
        };
    };
    responses: never;
    parameters: never;
    requestBodies: never;
    headers: never;
    pathItems: never;
}
export type $defs = Record<string, never>;
export interface operations {
    health_health_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
        };
    };
    ready_ready_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
        };
    };
    version_version_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": unknown;
                };
            };
        };
    };
    metrics_endpoint_metrics_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "text/plain": string;
                };
            };
        };
    };
    login_api_v1_auth_login_post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["LoginRequest"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["TokenResponse"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    me_api_v1_auth_me_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["MeResponse"];
                };
            };
        };
    };
    get_conditions_api_v1_sites__site_id__conditions_get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                site_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["SiteConditions"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    post_conditions_api_v1_sites__site_id__conditions_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                site_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["ConditionsUpdate"];
            };
        };
        responses: {
            /** @description Successful Response */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["TwinEnvironment"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    list_sites_api_v1_sites_get: {
        parameters: {
            query?: {
                limit?: number;
                offset?: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["Page_SiteDTO_"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    create_site_api_v1_sites_post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["SiteCreate"];
            };
        };
        responses: {
            /** @description Successful Response */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["SiteDTO"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    get_site_api_v1_sites__site_id__get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                site_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["SiteDTO"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    update_site_api_v1_sites__site_id__patch: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                site_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["SiteUpdate"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["SiteDTO"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    list_zones_api_v1_sites__site_id__zones_get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                site_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ZoneDTO"][];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    create_zone_api_v1_sites__site_id__zones_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                site_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["ZoneCreate"];
            };
        };
        responses: {
            /** @description Successful Response */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ZoneDTO"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    update_zone_api_v1_sites__site_id__zones__zone_id__patch: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                site_id: string;
                zone_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["ZoneUpdate"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ZoneDTO"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    list_operators_api_v1_operators_get: {
        parameters: {
            query?: {
                site_id?: string | null;
                limit?: number;
                offset?: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["Page_OperatorDTO_"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    create_operator_api_v1_operators_post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["OperatorCreate"];
            };
        };
        responses: {
            /** @description Successful Response */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["OperatorDTO"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    get_operator_api_v1_operators__operator_id__get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                operator_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["OperatorDTO"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    update_operator_api_v1_operators__operator_id__patch: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                operator_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["OperatorUpdate"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["OperatorDTO"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    list_machines_api_v1_machines_get: {
        parameters: {
            query?: {
                site_id?: string | null;
                machine_type?: ("EXCAVATOR" | "DUMPER" | "LOADER" | "DOZER" | "OTHER") | null;
                limit?: number;
                offset?: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["Page_MachineDTO_"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    create_machine_api_v1_machines_post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["MachineCreate"];
            };
        };
        responses: {
            /** @description Successful Response */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["MachineDTO"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    get_machine_api_v1_machines__machine_id__get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                machine_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["MachineDTO"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    update_machine_api_v1_machines__machine_id__patch: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                machine_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["MachineUpdate"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["MachineDTO"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    create_task_api_v1_tasks_post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["TaskCreate"];
            };
        };
        responses: {
            /** @description Successful Response */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["TaskDTO"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    get_task_api_v1_tasks__task_id__get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                task_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["TaskDTO"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    update_task_api_v1_tasks__task_id__patch: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                task_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["TaskUpdate"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["TaskDTO"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    list_site_tasks_api_v1_sites__site_id__tasks_get: {
        parameters: {
            query?: {
                status?: ("PLANNED" | "ASSIGNED" | "IN_PROGRESS" | "PAUSED" | "COMPLETED" | "CANCELLED") | null;
                date?: string | null;
            };
            header?: never;
            path: {
                site_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["TaskDTO"][];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    assign_task_api_v1_tasks__task_id__assign_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                task_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["AssignRequest"];
            };
        };
        responses: {
            /** @description Successful Response */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["AssignmentDTO"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    create_assignment_api_v1_assignments_post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["AssignmentCreate"];
            };
        };
        responses: {
            /** @description Successful Response */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["AssignmentDTO"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    patch_assignment_api_v1_assignments__assignment_id__patch: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                assignment_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["AssignmentUpdate"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["AssignmentDTO"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    operator_tasks_today_api_v1_operators__operator_id__tasks_today_get: {
        parameters: {
            query?: {
                date?: string | null;
            };
            header?: never;
            path: {
                operator_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["TodayTask"][];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    confirm_machine_api_v1_operators__operator_id__machine_confirm_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                operator_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["ConfirmMachineRequest"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ConfirmMachineResponse"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    get_precheck_api_v1_machines__machine_id__precheck_get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                machine_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["PrecheckTemplateDTO"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    post_precheck_api_v1_machines__machine_id__precheck_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                machine_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["PrecheckSubmit"];
            };
        };
        responses: {
            /** @description Successful Response */
            201: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["PrecheckResultDTO"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    start_task_api_v1_tasks__task_id__start_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                task_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["TaskActionResponse"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    pause_task_api_v1_tasks__task_id__pause_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                task_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["TaskActionResponse"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    resume_task_api_v1_tasks__task_id__resume_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                task_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["TaskActionResponse"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    complete_task_api_v1_tasks__task_id__complete_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                task_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["TaskActionResponse"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    task_summary_api_v1_tasks__task_id__summary_get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                task_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["TaskSummary"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    post_telemetry_api_v1_telemetry_post: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["TelemetryBatch"];
            };
        };
        responses: {
            /** @description Successful Response */
            202: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["IngestResult"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    get_machine_telemetry_api_v1_machines__machine_id__telemetry_get: {
        parameters: {
            query?: {
                from?: string | null;
                to?: string | null;
                limit?: number;
            };
            header?: never;
            path: {
                machine_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["TelemetryPoint"][];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    get_operator_twin_api_v1_operators__operator_id__twin_get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                operator_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["OperationalTwin"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    get_site_twin_api_v1_sites__site_id__twin_get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                site_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["SiteTwin"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    get_machine_state_api_v1_machines__machine_id__state_get: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                machine_id: string;
            };
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["TwinMachineState"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
}
