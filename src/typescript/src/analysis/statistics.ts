
import { parse } from "csv-parse/sync";

export interface StatisticsResult {
    totalEvents: number;
    scenarioCounts: Record<string, number>;
    averageDurationSeconds: number | null;
    minAcceleration: number | null;
    maxAcceleration: number | null;
    maxAbsJerk: number | null;
}

export function calculateStatistics(
    csvContent: string
): StatisticsResult {

    const records = parse(csvContent, {
        columns: true,
        skip_empty_lines: true,
        trim: true
    }) as Record<string, string>[];

    const scenarioCounts: Record<string, number> = {};

    const durations: number[] = [];
    const accelerations: number[] = [];
    const jerks: number[] = [];

    for (const record of records) {

        // Count events by scenario
        const scenario = record["scenario"];

        if (scenario) {
            scenarioCounts[scenario] =
                (scenarioCounts[scenario] ?? 0) + 1;
        }

        // Collect valid durations
        const duration = Number(record["duration_seconds"]);

        if (
            record["duration_seconds"]?.trim() !== "" &&
            Number.isFinite(duration)
        ) {
            durations.push(duration);
        }

        // Collect minimum and maximum acceleration values
        for (const column of [
            "min_acceleration_m_s2",
            "max_acceleration_m_s2"
        ]) {
            const value = Number(record[column]);

            if (
                record[column]?.trim() !== "" &&
                Number.isFinite(value)
            ) {
                accelerations.push(value);
            }
        }

        // Collect jerk values
        const jerk = Number(record["max_abs_jerk_m_s3"]);

        if (
            record["max_abs_jerk_m_s3"]?.trim() !== "" &&
            Number.isFinite(jerk)
        ) {
            jerks.push(jerk);
        }
    }

    const averageDuration = durations.length > 0
        ? durations.reduce((sum, value) => sum + value, 0)
            / durations.length
        : null;

    return {
        totalEvents: records.length,
        scenarioCounts,

        averageDurationSeconds: averageDuration,

        minAcceleration: accelerations.length > 0
            ? Math.min(...accelerations)
            : null,

        maxAcceleration: accelerations.length > 0
            ? Math.max(...accelerations)
            : null,

        maxAbsJerk: jerks.length > 0
            ? Math.max(...jerks)
            : null
    };
}
