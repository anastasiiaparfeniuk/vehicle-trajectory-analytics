
import { StatisticsResult } from "../analysis/statistics";

const nodeRequire = eval("require") as (moduleName: string) => {
    mkdirSync: (path: string, options: { recursive: boolean }) => void;
    writeFileSync: (path: string, data: string, encoding: string) => void;
    dirname: (path: string) => string;
};
const { mkdirSync, writeFileSync, dirname } = nodeRequire("fs");

export function generateJsonReport(
    statistics: StatisticsResult,
    outputPath: string
): void {

    const report = {
        generatedAt: new Date().toISOString(),
        ...statistics
    };

    const directory = dirname(outputPath);

    mkdirSync(directory, { recursive: true });

    writeFileSync(
        outputPath,
        JSON.stringify(report, null, 4),
        "utf-8"
    );

    console.log("JSON report created:", outputPath);
}
