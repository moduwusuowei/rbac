import { test as base, expect } from '@playwright/test';

const fs = require('fs');
const path = require('path');

const coverageDir = path.resolve(process.cwd(), 'coverage');

export const test = base.extend({
  context: async ({ context }, use) => {
    await use(context);
  },
  page: async ({ page }, use, testInfo) => {
    const coverageJs = await page.context().newCDPSession(page);
    await coverageJs.send('Profiler.enable');
    await coverageJs.send('Profiler.startPreciseCoverage', {
      callCount: true,
      detailed: true,
    });

    await use(page);

    const coverage = await coverageJs.send('Profiler.takePreciseCoverage');
    const outputCoverage = [];

    for (const entry of coverage.result) {
      if (entry.url.includes('localhost') && !entry.url.includes('node_modules')) {
        outputCoverage.push(entry);
      }
    }

    if (outputCoverage.length > 0) {
      fs.mkdirSync(coverageDir, { recursive: true });
      const coverageFile = path.join(
        coverageDir,
        `coverage-${Date.now()}-${testInfo.workerIndex}.json`
      );
      fs.writeFileSync(coverageFile, JSON.stringify(outputCoverage));
    }

    await coverageJs.send('Profiler.stopPreciseCoverage');
  },
});

export { expect };
