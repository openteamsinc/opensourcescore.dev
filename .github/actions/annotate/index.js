const fs = require('fs/promises');
const core = require('@actions/core');

// Validate package names using a regex (for valid package name characters)
function isValidPackageName(packageName) {
    const packageNamePattern = /^[a-zA-Z0-9._-]+$/;
    return packageNamePattern.test(packageName);
}

function stripVersion(packageLine) {
    return packageLine.split(/[<>=~!]/)[0].trim();
}

function processPackageLine(line) {
    const cleanLine = line.split('#')[0].trim();
    if (!cleanLine || cleanLine.startsWith('-')) return null;
    return stripVersion(cleanLine);
}

// Fetch package information from Score API
async function fetchPackageScore(packageName) {
    const url = `https://openteams-score.vercel.app/api/package/pypi/${packageName}`;
    try {
        const response = await fetch(url);
        if (response.ok) {
            return await response.json();
        } else {
            throw new Error(`Request failed with status code ${response.status}`);
        }
    } catch (error) {
        throw new Error(`Error fetching package ${packageName}: ${error.message}`);
    }
}

async function annotatePackage(packageName) {
    try {
        const response = await fetchPackageScore(packageName);
        if (response && response.source) {
            const { maturity, health_risk } = response.source;
            const maturityValue = maturity ? maturity.value : 'Unknown';
            const healthRiskValue = health_risk ? health_risk.value : 'Unknown';

            let recommendation = '';

            if (maturityValue === 'Mature' && healthRiskValue === 'Healthy') {
                recommendation = 'This package is likely to enhance stability and maintainability with minimal risks.';
            } else if (maturityValue === 'Mature' && healthRiskValue === 'Moderate Risk') {
                recommendation = 'The package is stable but may introduce some moderate risks.';
            } else if (maturityValue === 'Mature' && healthRiskValue === 'High Risk') {
                recommendation = 'The package is stable but introduces high risks.';
            } else if (maturityValue === 'Developing' && healthRiskValue === 'Healthy') {
                recommendation = 'The package is in development but poses low risks.';
            } else if (maturityValue === 'Experimental' || healthRiskValue === 'High Risk') {
                recommendation = 'This package may pose significant risks to stability and maintainability.';
            } else if (maturityValue === 'Legacy') {
                recommendation = 'This package is legacy and may not be stable, consider alternatives.';
            } else {
                recommendation = 'Insufficient data to make an informed recommendation.';
            }

            core.notice(`Package ${packageName}: (Maturity: ${maturityValue}, Health: ${healthRiskValue}). ${recommendation}`);
            core.setOutput(packageName, recommendation)
        } else {
            core.error(`Package ${packageName} not found.`);
            core.setOutput(packageName, 'Package not found.')
        }
    } catch (error) {
        core.error(`Error looking up package ${packageName}: ${error.message}`);
        core.setOutput(packageName, `Error: ${error.message}`)
    }
}

async function run() {
    const filePath = 'requirements.txt';
    const ecosystem = core.getInput('package-ecosystem', { required: true });

    // Check if the ecosystem is supported
    if (ecosystem !== 'pip') {
        core.setFailed(`Unsupported package ecosystem: ${ecosystem}`);
        return;
    }

    try {
        // Read the file asynchronously
        const packages = (await fs.readFile(filePath, 'utf-8')).split('\n').filter(pkg => pkg);

        for (const packageLine of packages) {
            const packageName = processPackageLine(packageLine);

            if (packageName) {
                if (!isValidPackageName(packageName)) {
                    core.error(`Invalid package name: ${packageName}`);
                    continue;
                }
                await annotatePackage(packageName);
            }
        }
    } catch (error) {
        core.setFailed(`Failed to read ${filePath}: ${error.message}`);
    }
}

run();
