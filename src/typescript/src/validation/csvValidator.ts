
import { parse } from "csv-parse/sync";

export interface ValidationResult {
    valid: boolean;
    rowCount: number;
    errors: string[];
}

const REQUIRED_COLUMNS = [
    "run_index",
    "id",
    "scenario",
    "start_time",
    "end_time",
    "event_time",
    "duration_seconds",
    "sample_count",
    "previous_lane",
    "new_lane"
];

const NUMERIC_COLUMNS = [
    "run_index",
    "id",
    "start_time",
    "end_time",
    "event_time",
    "duration_seconds",
    "sample_count",
    "min_acceleration_m_s2",
    "max_acceleration_m_s2",
    "max_abs_jerk_m_s3",
    "previous_lane",
    "new_lane"
];

export function validateCsv(csvContent: string): ValidationResult {
    const errors: string[] = [];

    const records = parse(csvContent, {
        columns: true,
        skip_empty_lines: true,
        trim: true
    }) as Record<string, string>[];

    if (records.length === 0) {
        return {
            valid: false,
            rowCount: 0,
            errors: ["CSV contains no data rows."]
        };
    }

    const headers = Object.keys(records[0]);

    const missingColumns = REQUIRED_COLUMNS.filter(
        column => !headers.includes(column)
    );

    if (missingColumns.length > 0) {
        return {
            valid: false,
            rowCount: records.length,
            errors: [
                `Missing columns: ${missingColumns.join(", ")}`
            ]
        };
    }

    records.forEach((record, index) => {
        const rowNumber = index + 2;
        const scenario = record["scenario"];

        // Common required values
        for (const column of ["run_index", "id", "scenario"]) {
            if (!record[column]?.trim()) {
                errors.push(
                    `Row ${rowNumber}: ${column} is empty.`
                );
            }
        }

        // Lane changes are instantaneous transitions
        const requiredValues = scenario === "lane_change"
            ? ["event_time", "previous_lane", "new_lane"]
            : [
                "start_time",
                "end_time",
                "duration_seconds",
                "sample_count"
            ];

        for (const column of requiredValues) {
            if (!record[column]?.trim()) {
                errors.push(
                    `Row ${rowNumber}: ${column} is empty.`
                );
            }
        }

        // Validate numeric values when present
        for (const column of NUMERIC_COLUMNS) {
            const value = record[column];

            if (
                value !== undefined &&
                value.trim() !== "" &&
                !Number.isFinite(Number(value))
            ) {
                errors.push(
                    `Row ${rowNumber}: ${column} is not numeric.`
                );
            }
        }
    });

    return {
        valid: errors.length === 0,
        rowCount: records.length,
        errors
    };
}
