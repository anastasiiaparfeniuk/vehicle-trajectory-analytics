
import { describe, it, expect } from "vitest";
import { validateCsv } from "./csvValidator";

const HEADER = [
    "run_index",
    "id",
    "scenario",
    "start_time",
    "end_time",
    "event_time",
    "duration_seconds",
    "sample_count",
    "min_acceleration_m_s2",
    "max_acceleration_m_s2",
    "max_abs_jerk_m_s3",
    "lane_labels",
    "previous_lane",
    "new_lane"
].join(",");

describe("validateCsv", () => {

    it("accepts a valid acceleration event", () => {
        const csv = HEADER +
            "\n1,10,rapid_acceleration,100,102,,2,20,-1,3,2,1;2,,";

        const result = validateCsv(csv);

        expect(result.valid).toBe(true);
        expect(result.rowCount).toBe(1);
        expect(result.errors).toHaveLength(0);
    });

    it("accepts a lane change without duration", () => {
        const csv = HEADER +
            "\n1,20,lane_change,,,105,,, , , ,1;2,1,2";

        const result = validateCsv(csv);

        expect(result.valid).toBe(true);
        expect(result.errors).toHaveLength(0);
    });

    it("rejects an empty required value", () => {
        const csv = HEADER +
            "\n1,,rapid_acceleration,100,102,,2,20,-1,3,2,1;2,,";

        const result = validateCsv(csv);

        expect(result.valid).toBe(false);
        expect(result.errors.some(
            error => error.includes("id is empty")
        )).toBe(true);
    });

    it("rejects a non-numeric value in a numeric column", () => {
        const csv = HEADER +
            "\n1,10,rapid_acceleration,abc,102,,2,20,-1,3,2,1;2,,";

        const result = validateCsv(csv);

        expect(result.valid).toBe(false);
        expect(result.errors.some(
            error => error.includes("start_time is not numeric")
        )).toBe(true);
    });

    it("rejects a CSV with missing columns", () => {
        const csv =
            "run_index,id,scenario\n" +
            "1,10,rapid_acceleration";

        const result = validateCsv(csv);

        expect(result.valid).toBe(false);
        expect(result.errors[0]).toContain("Missing columns");
    });

});
