import { calculateStatistics } from "./analysis/statistics";
import { generateJsonReport } from "./reports/reportGenerator";
declare const require: (moduleName: string) => any;
declare const __dirname: string;
declare const process: { exitCode: number };
const fs = require("fs");
const path = require("path");

import { validateCsv } from "./validation/csvValidator";

const projectRoot = path.resolve(__dirname, "../../..");

const csvPath = path.join(
    projectRoot,
    "data",
    "processed",
    "scenario_event_summary.csv"
);

console.log("================================");
console.log("Vehicle Trajectory Analytics");
console.log("================================");

if (!fs.existsSync(csvPath)) {
    console.error("CSV file not found:", csvPath);
    process.exitCode = 1;
} else {
    const csvContent = fs.readFileSync(csvPath, "utf-8");

    const result = validateCsv(csvContent);
    const statistics = calculateStatistics(csvContent);
    const reportPath = path.join(
        projectRoot,
        "data",
        "processed",
        "summary_report.json"
    );

    generateJsonReport(statistics, reportPath);
    console.log("File:", csvPath);
    console.log("Rows:", result.rowCount);
    console.log("Validation:", result.valid ? "PASSED" : "FAILED");

    if (result.errors.length > 0) {
        console.error("\nValidation errors:");

        for (const error of result.errors.slice(0, 20)) {
            console.error("-", error);
        }

        if (result.errors.length > 20) {
            console.error(
                `...and ${result.errors.length - 20} more errors.`
            );
        }
    }

    if (!result.valid) {
        process.exitCode = 1;
    }
    console.log("\n================================");
console.log("Dataset Statistics");
console.log("================================");

console.log("Total events:", statistics.totalEvents);

console.log("\nEvents by scenario:");

for (const [scenario, count] of Object.entries(
    statistics.scenarioCounts
)) {
    console.log(`- ${scenario}: ${count}`);
}

console.log(
    "\nAverage duration:",
    statistics.averageDurationSeconds?.toFixed(2) ?? "N/A",
    "seconds"
);

console.log("Minimum acceleration:",
    statistics.minAcceleration?.toFixed(2) ?? "N/A",
    "m/s²"
);

console.log("Maximum acceleration:",
    statistics.maxAcceleration?.toFixed(2) ?? "N/A",
    "m/s²"
);

console.log("Maximum absolute jerk:",
    statistics.maxAbsJerk?.toFixed(2) ?? "N/A",
    "m/s³"
);
}

