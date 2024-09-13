const fs = require('fs/promises');

// Validate package names using a regex (for valid package name characters)
function isValidPackageName(packageName) {
    const packageNamePattern = /^[a-zA-Z0-9._-]+$/;
    return packageNamePattern.test(packageName);
}

function stripVersion(packageLine) {
    return packageLine.split(/[<>=~!]/)[0].trim();
}

// Process and clean up each line from requirements.txt
function processPackageLine(line) {
    const cleanLine = line.split('#')[0].trim();  // Remove inline comments and whitespace
    if (!cleanLine || cleanLine.startsWith('-')) return null;  // Skip empty lines, comments, or flags
    return stripVersion(cleanLine);  // Strip versioning
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
            
            console.log(`::notice file=requirements.txt::Package ${packageName} found. (Maturity: ${maturityValue}, Health: ${healthRiskValue})`);
        } else {
            console.log(`::error file=requirements.txt::Package ${packageName} not found.`);
        }
    } catch (error) {
        console.log(`::error file=requirements.txt::Error looking up package ${packageName}: ${error.message}`);
    }
}

async function run() {
    const filePath = 'requirements.txt';
    const ecosystem = process.env.PACKAGE_ECOSYSTEM || 'pip';

    // Check if the ecosystem is supported
    if (ecosystem !== 'pip') {
        console.log(`::error::Unsupported package ecosystem: ${ecosystem}`);
        return;
    }

    try {
        // Read the file asynchronously
        const lines = (await fs.readFile(filePath, 'utf-8')).split('\n');
        
        for (const line of lines) {
            const packageName = processPackageLine(line);

            if (packageName) {
                if (!isValidPackageName(packageName)) {
                    console.log(`::error file=requirements.txt::Invalid package name: ${packageName}`);
                    continue;
                }
                await annotatePackage(packageName);
            }
        }
    } catch (error) {
        console.log(`::error::Failed to read ${filePath}: ${error.message}`);
    }
}

run();
