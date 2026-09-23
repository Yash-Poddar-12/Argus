// GENERATED from contracts/openapi/m00-platform.yaml by packages/api-client/scripts/generate.mjs. Do not edit.
export interface paths {
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
}
export type webhooks = Record<string, never>;
export interface components {
    schemas: {
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
}
